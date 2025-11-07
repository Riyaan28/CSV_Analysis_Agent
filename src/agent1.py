"""
LangChain agent implementation for CSV analysis
"""
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.llms.base import LLM
from typing import Any, List, Optional, Dict
from pydantic import Field
import pandas as pd
import numpy as np
import re
from src.ollama_client import OllamaClient
from src.rag_module import RAGModule
from src.cache_manager import CacheManager


class OllamaLLM(LLM):
    """Custom LLM wrapper for Ollama"""
    
    ollama_client: OllamaClient = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, model_name: str = "llama3.2:latest", **kwargs):
        super().__init__(**kwargs)
        self.ollama_client = OllamaClient(model_name)
    
    @property
    def _llm_type(self) -> str:
        return "ollama"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call Ollama with prompt"""
        response = self.ollama_client.generate(prompt)
        return response


class CSVAnalysisAgent:
    """Agent for analyzing CSV data with natural language"""
    
    def __init__(self, model_name: str = "llama3.2:latest"):
        """
        Initialize the agent
        
        Args:
            model_name: Ollama model to use
        """
        self.model_name = model_name
        self.ollama_client = OllamaClient(model_name)
        self.rag_module = RAGModule()
        self.cache_manager = CacheManager()
        self.df: Optional[pd.DataFrame] = None
        self.dataset_hash: Optional[str] = None
        self.agent = None
        self.context_used: List[str] = []
    
    def initialize_agent(self, df: pd.DataFrame, dataset_hash: str):
        """
        Initialize agent with dataframe
        
        Args:
            df: Pandas dataframe to analyze
            dataset_hash: Hash of the dataset for caching
        """
        try:
            self.df = df
            self.dataset_hash = dataset_hash
            
            # Build RAG index
            print("Building RAG index...")
            self.rag_module.build_index(df)
            print("RAG index built successfully")
            
            # Create LangChain pandas dataframe agent
            print("Creating pandas dataframe agent...")
            llm = OllamaLLM(model_name=self.model_name)
            
            # Custom error handler for parsing issues
            def handle_error(error) -> str:
                """Handle parsing errors gracefully"""
                error_str = str(error)
                print(f"⚠ Parsing error occurred: {error_str[:200]}")
                return "I encountered a formatting issue. Let me try a different approach to answer your question."
            
            # Use zero-shot-react-description with optimized configuration
            self.agent = create_pandas_dataframe_agent(
                llm=llm,
                df=df,
                agent_type="zero-shot-react-description",
                verbose=True,  # Show execution steps for debugging
                allow_dangerous_code=True,  # Required for code execution
                max_iterations=5,  # Allow more iterations for complex queries
                handle_parsing_errors=handle_error,  # Custom error handler
                include_df_in_prompt=True,  # Include DataFrame info in prompt
                prefix="""You are a data analysis expert working with a pandas DataFrame named `df`.

IMPORTANT: Follow the ReAct format EXACTLY:
- Question: the input question
- Thought: think about what to do
- Action: python_repl_ast
- Action Input: the pandas code (ONE LINE ONLY)
- Observation: (will be filled automatically)
- Repeat Thought/Action/Observation as needed
- When done: Thought: I now know the final answer
- Final Answer: [the result data ONLY]

RULES FOR ACTION INPUT:
- Write ONLY executable pandas code
- ONE single line of code
- NO print() statements
- NO extra text or explanations
- Just the pandas expression

EXAMPLES:
Question: Show first 3 rows
Thought: I need to show the first 3 rows of the dataframe
Action: python_repl_ast
Action Input: df.head(3)

Question: How many missing values?
Thought: I need to count null values in each column
Action: python_repl_ast
Action Input: df.isnull().sum()

Question: Filter rows where name is 'Jane Doe'
Thought: I need to filter the dataframe based on the name column
Action: python_repl_ast
Action Input: df[df['name'] == 'Jane Doe']

The DataFrame has these columns: {columns}
""".replace('{columns}', ', '.join(df.columns.tolist()))
            )
            print("✅ Agent created successfully")
            
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
            raise
    
    def query(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query using LangChain pandas dataframe agent
        
        Args:
            user_query: Natural language query
            
        Returns:
            Dictionary with response and metadata
        """
        if self.df is None:
            return {
                "response": "No dataset loaded. Please upload a CSV file first.",
                "cache_hit": False,
                "context": []
            }
        
        # Check cache
        cached_response, cache_hit = self.cache_manager.get_cached_response(
            user_query, self.dataset_hash
        )
        
        if cache_hit:
            return {
                "response": cached_response,
                "cache_hit": True,
                "context": []
            }
        
        # Get relevant context from RAG
        context = self.rag_module.get_context_string(user_query, top_k=5)
        context_docs, _ = self.rag_module.retrieve_context(user_query, top_k=5)
        self.context_used = context_docs
        
        response = None
        
        # PRIMARY: Use LangChain pandas dataframe agent
        try:
            # Build query with clear instructions
            enhanced_query = f"""Answer this query about the dataset: {user_query}

IMPORTANT INSTRUCTIONS:
1. Write and execute pandas code using the 'df' DataFrame
2. Return the RESULT in clean format (tables, numbers, lists)
3. For tables: ensure proper formatting
4. For numbers: format with appropriate precision
5. NO explanations, just the data

Dataset Context (for reference):
{context}"""

            print(f"\n{'='*60}")
            print(f"Query: {user_query}")
            print(f"{'='*60}")
            
            # Invoke LangChain agent
            result = self.agent.invoke({"input": enhanced_query})
            
            # Debug: Print intermediate steps if available
            if isinstance(result, dict):
                print(f"\n🔍 LANGCHAIN AGENT EXECUTION DEBUG:")
                print(f"{'='*60}")
                
                # Print intermediate steps (Thought/Action/Observation)
                if 'intermediate_steps' in result:
                    for i, step in enumerate(result['intermediate_steps'], 1):
                        print(f"\n--- Step {i} ---")
                        if isinstance(step, tuple) and len(step) == 2:
                            action, observation = step
                            print(f"Action Tool: {action.tool if hasattr(action, 'tool') else 'N/A'}")
                            print(f"Action Input: {action.tool_input if hasattr(action, 'tool_input') else action}")
                            print(f"Observation: {observation}")
                
                # Print full result structure
                print(f"\n📦 Full Result Structure:")
                for key, value in result.items():
                    if key != 'intermediate_steps':
                        print(f"  {key}: {value}")
                
                print(f"{'='*60}\n")
            
            # Extract response
            if isinstance(result, dict) and 'output' in result:
                response = result['output']
            else:
                response = str(result)
            
            print(f"LangChain Agent Response (raw):\n{response}")
            print(f"{'='*60}\n")
            
            # Clean the response to remove LangChain artifacts
            response = self._clean_langchain_response(response)
            
            print(f"✅ Cleaned Response:\n{response}")
            print(f"{'='*60}\n")
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ LangChain agent error: {error_msg[:300]}")
            print(f"Using direct execution fallback...")
            
            # FALLBACK: Direct code execution with enhanced capabilities
            try:
                code = self._generate_pandas_code(user_query, context)
                if code:
                    print(f"Generated fallback code: {code}")
                    response = self._execute_pandas_code(code)
                    print(f"Fallback response: {response}")
                else:
                    response = "I couldn't generate appropriate code for that query. Please try rephrasing."
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {str(fallback_error)}")
                response = f"Error: Unable to process query. {str(fallback_error)}"
        
        # Cache the response
        if response:
            self.cache_manager.cache_response(user_query, self.dataset_hash, response)
        
        return {
            "response": response if response else "No result generated",
            "cache_hit": False,
            "context": context_docs
        }
    
    def _clean_langchain_response(self, response: str) -> str:
        """
        Clean LangChain agent response to extract only the actual data/result
        
        Args:
            response: Raw response from LangChain agent
            
        Returns:
            Cleaned response with only the result
        """
        if not response:
            return response
        
        response = response.strip()
        
        # Remove "Final Answer:" prefix (common in ReAct agents)
        if response.lower().startswith('final answer:'):
            response = response[len('final answer:'):].strip()
        
        # If response contains markdown table, extract and format it
        if '|' in response and ('---' in response or response.count('|') > 6):
            lines = response.split('\n')
            table_lines = []
            
            for line in lines:
                if '|' in line or ('---' in line and table_lines):
                    table_lines.append(line)
                elif table_lines and line.strip().startswith('*'):
                    # Include notes like "*Showing first 20 rows*"
                    table_lines.append(line)
                elif table_lines and not line.strip():
                    # Empty line after table
                    continue
                elif table_lines:
                    # Table has ended
                    break
            
            if table_lines:
                return '\n'.join(table_lines).strip()
        
        # Use the comprehensive cleaner
        return self._clean_response(response)
    
    def _build_enhanced_prompt(self, query: str, context: str) -> str:
        """
        Build prompt that guides LLM to generate pandas code and return clean results
        
        Args:
            query: User query
            context: Retrieved context from RAG
            
        Returns:
            Enhanced prompt
        """
        prompt = f"""You are a data analyst AI. You have access to a pandas DataFrame called 'df'.

Dataset Context:
{context}

User Query: {query}

INSTRUCTIONS FOR CODE GENERATION:
1. Generate pandas code to answer the query
2. Execute the code and get the result
3. Return ONLY the final result in clean format
4. For tables: Use markdown table format or show df.to_markdown()
5. For numbers: Show with proper formatting (e.g., "Sum: 123,456.78")
6. For lists: Show in bullet points or clean format
7. Do NOT show the code itself
8. Do NOT show intermediate steps
9. Do NOT show explanations unless specifically asked

Answer the query by executing pandas code on df:"""
        
        return prompt
    
    def _clean_response(self, response: str) -> str:
        """
        Professional response cleaning to remove all LLM artifacts, thinking process,
        and extract only the actual data/result.
        
        Args:
            response: Raw response string from LLM
            
        Returns:
            Cleaned response with only the actual result
        """
        if not response:
            return response
        
        response = response.strip()
        
        # Step 1: Remove common LLM prefixes (case-insensitive)
        prefixes_to_remove = [
            'final answer:', 'answer:', 'result:', 'output:', 'response:',
            'here is the answer:', "here's the answer:", 'the answer is:',
            'here is the result:', "here's the result:", 'the result is:',
            'here you go:', 'here it is:', 'the output is:',
            'based on the', 'according to', 'as per the'
        ]
        
        response_lower = response.lower()
        for prefix in prefixes_to_remove:
            if response_lower.startswith(prefix):
                # Remove prefix and everything before the colon/period
                response = response[len(prefix):].strip()
                response_lower = response.lower()
                break
        
        # Step 2: Extract markdown tables if present (they should be preserved)
        # A markdown table has | characters and at least one separator line with ---
        has_table = '|' in response and ('---' in response or response.count('|') > 6)
        
        if has_table:
            # Extract just the table part
            lines = response.split('\n')
            table_lines = []
            in_table = False
            
            for line in lines:
                if '|' in line:
                    in_table = True
                    table_lines.append(line)
                elif in_table and line.strip() == '':
                    # Empty line might be part of table formatting
                    continue
                elif in_table and '---' in line:
                    # Separator line
                    table_lines.append(line)
                elif in_table and '|' not in line:
                    # Table has ended, check if this is a note
                    if line.strip().startswith('*') or 'showing' in line.lower():
                        table_lines.append(line)
                    break
            
            if table_lines:
                return '\n'.join(table_lines).strip()
        
        # Step 3: Remove duplicate information
        # Sometimes LLM outputs: "42\nFinal Answer: 42" or similar
        lines = response.split('\n')
        if len(lines) > 1:
            first_line = lines[0].strip()
            rest_lines = [l.strip() for l in lines[1:] if l.strip()]
            
            # Check if first line is a simple value that's repeated
            if len(first_line) < 100 and rest_lines:
                for rest_line in rest_lines:
                    # If any later line contains the first line, it might be duplicate
                    if first_line in rest_line and rest_line != first_line:
                        # Remove prefix from the later line and use that
                        for prefix in prefixes_to_remove:
                            if rest_line.lower().startswith(prefix):
                                cleaned = rest_line[len(prefix):].strip()
                                if cleaned == first_line:
                                    response = first_line
                                    break
        
        # Step 4: Remove explanation text (anything after first complete result)
        # If response has a clean result followed by explanation, keep only result
        if '\n\n' in response:
            parts = response.split('\n\n')
            # First part is usually the actual answer
            first_part = parts[0].strip()
            # Check if first part looks like a complete answer
            if (first_part and 
                not first_part.lower().startswith(('note:', 'explanation:', 'this shows'))):
                response = first_part
        
        # Step 5: Remove thinking patterns like "Let me...", "I'll...", "First..."
        thinking_patterns = [
            r'^(let me|i will|i\'ll|first|to answer this|to get this).+?\n',
            r'^(looking at|analyzing|checking|examining).+?\n'
        ]
        
        import re
        for pattern in thinking_patterns:
            response = re.sub(pattern, '', response, flags=re.IGNORECASE | re.MULTILINE)
        
        # Step 6: Remove code blocks if present (user asked for results, not code)
        if '```' in response:
            # Extract content between code blocks
            parts = response.split('```')
            # Usually format is: [text] ``` [code] ``` [result]
            # We want the result after the code block
            if len(parts) >= 3:
                # Take the part after last code block
                response = parts[-1].strip()
            elif len(parts) == 2:
                # Only one code block, take the part outside it
                if parts[0].strip():
                    response = parts[0].strip()
                else:
                    response = parts[1].strip()
        
        # Step 7: Clean up markdown bold/italic that might wrap the entire response
        response = response.strip('*_')
        
        # Step 8: Final cleanup - remove any leading/trailing whitespace
        response = response.strip()
        
        return response
    
    def _generate_pandas_code(self, query: str, context: str) -> Optional[str]:
        """
        Ask LLM to generate pandas code for the query with case-insensitive string matching
        
        Args:
            query: User query
            context: RAG context
            
        Returns:
            Pandas code string or None
        """
        # Get actual column names from the dataframe
        columns_list = ', '.join(self.df.columns.tolist())
        
        prompt = f"""TASK: Generate pandas code ONLY. Nothing else.

DataFrame 'df' has columns: {columns_list}

Query: {query}

CRITICAL RULES:
- Return ONLY executable pandas code
- ONE line of code starting with 'df' or '(df'  
- NO "Thought:", "Action:", "Observation:"
- NO explanations, descriptions, or comments
- NO markdown code blocks
- NO text before or after the code
- For string comparisons, ALWAYS use .str.lower() for case-insensitive matching
- Use ACTUAL column names from the DataFrame

RETURN FORMAT RULES:
- If asked "how many", return COUNT (use len() or .shape[])
- If asked "show" or "list" or "display", return the actual DATA
- If asked "what are", return the actual items
- If asked "distribution" or "value_counts", return a TABLE with counts
- For string filtering, use: df[df['column'].str.lower() == 'value']

COMPREHENSIVE EXAMPLES (replace 'column_name' with actual column names):

# Dataset Information
Q: "What columns are in this dataset?" → df.columns.tolist()
Q: "How many rows and columns?" → df.shape
Q: "How many rows?" → len(df)
Q: "How many columns?" → len(df.columns)
Q: "What are the data types?" → df.dtypes.to_frame(name='Data Type')
Q: "Show column names" → df.columns.tolist()

# View Data
Q: "Show first row" → df.head(1)
Q: "Show first 5 rows" → df.head(5)
Q: "Show last 2 rows" → df.tail(2)
Q: "Display all data" → df
Q: "Show me the data" → df.head(20)
Q: "Show first 10 records" → df.head(10)

# View Columns
Q: "Show 3 columns" → df.iloc[:, :3]
Q: "Show first 4 columns" → df.iloc[:, :4]
Q: "Show last 2 columns" → df.iloc[:, -2:]

# Statistical Analysis
Q: "Show statistical summary" → df.describe()
Q: "Sum of salary column" → df['salary'].sum()
Q: "Average of age column" → df['age'].mean()
Q: "Median of price" → df['price'].median()
Q: "Min of age" → df['age'].min()
Q: "Max of salary" → df['salary'].max()
Q: "Standard deviation of salary" → df['salary'].std()

# Distribution & Value Counts (ALWAYS show as TABLE)
Q: "Show distribution of gender column" → df['gender'].value_counts().to_frame(name='Count')
Q: "Distribution of department" → df['department'].value_counts().to_frame(name='Count')
Q: "Value counts in status column" → df['status'].value_counts().to_frame(name='Count')
Q: "Frequency of category" → df['category'].value_counts().to_frame(name='Count')
Q: "How many of each gender?" → df['gender'].value_counts().to_frame(name='Count')
Q: "Count by department" → df['department'].value_counts().to_frame(name='Count')

# Unique Values
Q: "Unique values in gender" → df['gender'].unique().tolist()
Q: "Unique departments" → df['department'].unique().tolist()
Q: "What are the unique values in status?" → df['status'].unique().tolist()
Q: "List unique categories" → df['category'].unique().tolist()
Q: "How many unique values in gender?" → df['gender'].nunique()

# String Filtering (CASE-INSENSITIVE - ALWAYS use .str.lower())
Q: "Show row where name is 'Jane Doe'" → df[df['name'].str.lower() == 'jane doe']
Q: "Show me row with name 'jane doe'" → df[df['name'].str.lower() == 'jane doe']
Q: "Filter by name 'JOHN SMITH'" → df[df['name'].str.lower() == 'john smith']
Q: "Rows with department 'Marketing'" → df[df['department'].str.lower() == 'marketing']
Q: "Find person named 'alice'" → df[df['name'].str.lower() == 'alice']
Q: "Show employees in 'IT'" → df[df['department'].str.lower() == 'it']
Q: "Filter status 'Active'" → df[df['status'].str.lower() == 'active']

# Aggregations (with case-insensitive string matching)
Q: "Count of Male in gender" → (df['gender'].str.lower() == 'male').sum()
Q: "How many Female in gender?" → (df['gender'].str.lower() == 'female').sum()
Q: "Count employees in Marketing" → (df['department'].str.lower() == 'marketing').sum()
Q: "How many active users?" → (df['status'].str.lower() == 'active').sum()

# Missing Values
Q: "Missing values" → df.isnull().sum().to_frame(name='Missing Values')
Q: "Null values" → df.isnull().sum().to_frame(name='Null Values')
Q: "How many missing values in each column?" → df.isnull().sum().to_frame(name='Missing Values')
Q: "Missing values per column" → df.isnull().sum().to_frame(name='Missing Values')
Q: "Count null values in each column" → df.isnull().sum().to_frame(name='Missing Values')
Q: "How many missing values total?" → df.isnull().sum().sum()
Q: "Total missing values" → df.isnull().sum().sum()

# Numeric Operations
Q: "Total of price column" → df['price'].sum()
Q: "Average age of employees" → df['age'].mean()
Q: "Highest salary" → df['salary'].max()
Q: "Lowest price" → df['price'].min()

# Sorting
Q: "Sort by salary descending" → df.sort_values('salary', ascending=False)
Q: "Sort by age ascending" → df.sort_values('age')
Q: "Top 5 highest salaries" → df.nlargest(5, 'salary')
Q: "Bottom 3 ages" → df.nsmallest(3, 'age')

YOUR CODE (one line only):"""

        try:
            code_response = self.ollama_client.generate(prompt)
            # Clean up the response AGGRESSIVELY to remove all LLM thinking
            code = code_response.strip()
            
            print(f"Raw LLM response: {code}")
            
            # FIRST: Remove any ReAct-style thinking (Thought:, Action:, Observation:)
            if 'Thought:' in code or 'Action:' in code or 'Observation:' in code:
                print("Detected ReAct-style output, filtering...")
                # This means LLM is trying to use agent format - reject this entirely
                # Try to extract just the code part
                lines = code.split('\n')
                for line in lines:
                    line = line.strip()
                    # Look for lines that contain actual pandas code
                    if 'df[' in line or 'df.' in line:
                        if not any(word in line.lower() for word in ['thought', 'action', 'observation', 'input']):
                            code = line
                            break
            
            # Remove code blocks if present
            if '```python' in code:
                code = code.split('```python')[1].split('```')[0].strip()
            elif '```' in code:
                code = code.split('```')[1].split('```')[0].strip()
            
            # Remove ALL text before actual code - look for df or common patterns
            # Split by newlines and find the first line that looks like code
            lines = code.split('\n')
            code_lines = []
            
            # Aggressive filtering: reject lines with thinking keywords
            reject_keywords = [
                'thought:', 'action:', 'observation:', 'final answer:', 'question:',
                'here is', 'here\'s', 'the code', 'to answer', 'this will',
                'you can use', 'we can', 'let me', 'i will', 'i need',
                'note:', 'explanation:', 'query:', 'output:', 'returns:', 
                'this code', 'for troubleshooting', 'visit:', 'http'
            ]
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Skip lines with reject keywords
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in reject_keywords):
                    continue
                    
                # Skip comments
                if line.startswith('#'):
                    continue
                    
                # Skip imports
                if line.startswith('import ') or line.startswith('from '):
                    continue
                
                # If line contains pandas code, it's valid
                if 'df[' in line or 'df.' in line or (line.startswith('(') and 'df' in line):
                    code_lines.append(line)
                    break  # Take only the first valid code line
            
            # Take first code line
            if code_lines:
                code = code_lines[0]
            else:
                # Fallback: look for any line with df in the entire response
                print("No code found in filtered lines, trying fallback...")
                for line in lines:
                    line_lower = line.strip().lower()
                    # Skip lines with agent format keywords
                    if any(word in line_lower for word in ['thought:', 'action:', 'observation:', 'final answer:']):
                        continue
                    if ('df[' in line or 'df.' in line) and not line.strip().startswith('#'):
                        code = line.strip()
                        print(f"Found code in fallback: {code}")
                        break
                
                if not code_lines and 'df' not in code:
                    # Last resort: try to generate again with even more explicit prompt
                    print("No valid code found, trying second attempt with simpler prompt...")
                    simple_prompt = f"""Return ONLY pandas code. No text, no explanation.

Query: {query}
DataFrame: df
Columns: {', '.join(self.df.columns.tolist())}

Code only:"""
                    
                    try:
                        retry_response = self.ollama_client.generate(simple_prompt)
                        # Extract first line with df in it
                        for line in retry_response.split('\n'):
                            if 'df' in line and not any(word in line.lower() for word in ['thought', 'action', 'observation']):
                                code = line.strip()
                                print(f"Second attempt code: {code}")
                                break
                    except:
                        pass
                
                if 'df' not in code:
                    print(f"No valid code found after all attempts: {code_response}")
                    return None
            
            print(f"After initial cleaning: {code}")
            
            # Reject invalid patterns
            invalid_patterns = [
                'pd.DataFrame(',  # Don't allow creating new DataFrames
                'df =',  # Don't allow reassigning df
                '{',  # Don't allow dictionary/set creation (usually part of DataFrame creation)
            ]
            
            for pattern in invalid_patterns:
                if pattern in code:
                    print(f"Rejected code with invalid pattern '{pattern}': {code}")
                    return None
            
            # Validate code contains 'df'
            if 'df' not in code:
                print(f"Generated code doesn't reference df: {code}")
                return None
            
            # Auto-fix common syntax issues
            # Fix missing parentheses for comparison + sum/count/mean operations
            # Pattern: df['col'] == 'value'.sum() -> (df['col'] == 'value').sum()
            if '==' in code or '!=' in code or '>' in code or '<' in code:
                # Check if there's a method call after the comparison
                if any(method in code for method in ['.sum()', '.count()', '.mean()', '.any()', '.all()']):
                    # If the comparison is not already wrapped in parentheses
                    if not code.startswith('(') or code.find(')') > code.find('.sum'):
                        # Find the comparison part
                        for op in ['==', '!=', '>=', '<=', '>', '<']:
                            if op in code:
                                parts = code.split(op, 1)
                                if len(parts) == 2:
                                    left = parts[0].strip()
                                    right = parts[1].strip()
                                    # Find where the value ends and method starts
                                    for method in ['.sum()', '.count()', '.mean()', '.any()', '.all()']:
                                        if method in right:
                                            value_part = right.split(method)[0].strip()
                                            method_part = method + right.split(method)[1] if len(right.split(method)) > 1 else method
                                            code = f"({left} {op} {value_part}){method_part}"
                                            print(f"Auto-corrected code: {code}")
                                            break
                                    break
            
            print(f"Final cleaned code: {code}")
            return code
            
        except Exception as e:
            print(f"Error generating code: {e}")
            return None
    
    def _format_result_professionally(self, result) -> str:
        """
        Professional formatting of pandas results into clean, consistent output.
        
        Args:
            result: Result from pandas code execution (DataFrame, Series, scalar, etc.)
            
        Returns:
            Professionally formatted string suitable for display
        """
        try:
            # Case 1: DataFrame - Convert to markdown table
            if isinstance(result, pd.DataFrame):
                if result.empty:
                    return "*(Empty result)*"
                
                # Limit rows for display
                if len(result) > 20:
                    markdown_table = result.head(20).to_markdown(index=False)
                    return f"{markdown_table}\n\n*Showing first 20 of {len(result)} rows*"
                else:
                    return result.to_markdown(index=False)
            
            # Case 2: Series - Convert to DataFrame then to markdown table
            elif isinstance(result, pd.Series):
                if result.empty:
                    return "*(Empty result)*"
                
                # Determine appropriate column name
                series_name = result.name if result.name is not None else "Value"
                
                # Convert to DataFrame with index as a column
                df_formatted = result.to_frame(name=series_name).reset_index()
                
                # Rename index column if it has no name or generic name
                if df_formatted.columns[0] == 'index' or df_formatted.columns[0] == 0:
                    # Try to infer a better name
                    if result.index.name:
                        df_formatted.columns = [result.index.name, series_name]
                    else:
                        # Use a generic but clear name
                        df_formatted.columns = ['Item', series_name]
                
                # Limit rows for display
                if len(result) > 20:
                    markdown_table = df_formatted.head(20).to_markdown(index=False)
                    return f"{markdown_table}\n\n*Showing first 20 of {len(result)} values*"
                else:
                    return df_formatted.to_markdown(index=False)
            
            # Case 3: Numeric values (int, float)
            elif isinstance(result, (int, float)):
                if isinstance(result, float):
                    # Format float with 2 decimal places and thousands separator
                    return f"**{result:,.2f}**"
                else:
                    # Format int with thousands separator
                    return f"**{result:,}**"
            
            # Case 3b: Numpy numeric types
            elif hasattr(result, 'item'):
                # Numpy scalar types (int64, float64, etc.)
                import numpy as np
                if isinstance(result, (np.integer, np.floating)):
                    val = result.item()  # Convert to Python native type
                    if isinstance(val, float):
                        return f"**{val:,.2f}**"
                    else:
                        return f"**{val:,}**"
            
            # Case 4: String
            elif isinstance(result, str):
                return result
            
            # Case 5: List/tuple/array
            elif isinstance(result, (list, tuple)):
                if len(result) == 0:
                    return "*(Empty list)*"
                elif len(result) <= 20:
                    # Show as comma-separated for short lists
                    return ', '.join(str(item) for item in result)
                else:
                    # Show first 20 items for long lists
                    preview = ', '.join(str(item) for item in result[:20])
                    return f"{preview}\n\n*Showing first 20 of {len(result)} items*"
            
            # Case 6: Numpy array
            elif hasattr(result, '__array__'):
                import numpy as np
                if isinstance(result, np.ndarray):
                    if result.size == 0:
                        return "*(Empty array)*"
                    elif result.size == 1:
                        # Single value
                        val = result.item()
                        if isinstance(val, (int, np.integer)):
                            return f"**{val:,}**"
                        elif isinstance(val, (float, np.floating)):
                            return f"**{val:,.2f}**"
                        else:
                            return str(val)
                    else:
                        # Convert to list and format
                        result_list = result.tolist()
                        return self._format_result_professionally(result_list)
            
            # Case 7: Boolean
            elif isinstance(result, bool):
                return '**Yes**' if result else '**No**'
            
            # Case 8: Tuple (like shape)
            elif isinstance(result, tuple):
                if len(result) == 2 and all(isinstance(x, int) for x in result):
                    # Likely a shape tuple
                    return f"**Rows: {result[0]:,}, Columns: {result[1]:,}**"
                else:
                    return str(result)
            
            # Case 9: Dictionary
            elif isinstance(result, dict):
                if len(result) == 0:
                    return "*(Empty dictionary)*"
                # Convert dict to DataFrame for nice table display
                try:
                    df = pd.DataFrame(list(result.items()), columns=['Key', 'Value'])
                    return df.to_markdown(index=False)
                except:
                    # Fallback to string representation
                    return str(result)
            
            # Default: Convert to string
            else:
                return str(result)
                
        except Exception as e:
            print(f"Error formatting result: {e}")
            return str(result)
    
    def _execute_pandas_code(self, code: str) -> str:
        """
        Safely execute pandas code and format the result professionally
        
        Args:
            code: Pandas code to execute
            
        Returns:
            Professionally formatted result string
        """
        try:
            # Create safe execution environment with essential builtins
            safe_builtins = {
                'len': len,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'int': int,
                'float': float,
                'str': str,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'sorted': sorted,
                'reversed': reversed,
                'any': any,
                'all': all,
            }
            
            safe_dict = {
                'df': self.df,
                'pd': pd,
                'np': __import__('numpy'),
                '__builtins__': safe_builtins
            }
            
            # Try to execute code with eval first (for single expressions)
            result = None
            try:
                result = eval(code, safe_dict)
                print(f"✓ eval() succeeded, result type: {type(result)}")
            except SyntaxError:
                # If eval fails, the code might be a statement or multi-line
                # Try exec instead
                print("⚠ eval() failed, trying exec()...")
                
                # For exec, we need to capture the last expression
                # Split by semicolons or newlines
                code_lines = [line.strip() for line in code.replace(';', '\n').split('\n') if line.strip()]
                
                if len(code_lines) == 1:
                    # Single line that failed eval - might be an assignment
                    exec(code, safe_dict)
                    if 'result' in safe_dict:
                        result = safe_dict['result']
                    else:
                        return "⚠ Code executed but produced no result. Please rephrase your query."
                else:
                    # Multiple lines - execute all and return the last one
                    for line in code_lines[:-1]:
                        exec(line, safe_dict)
                    
                    # Try to eval the last line to get result
                    try:
                        result = eval(code_lines[-1], safe_dict)
                    except:
                        # If that fails, just execute it
                        exec(code_lines[-1], safe_dict)
                        if 'result' in safe_dict:
                            result = safe_dict['result']
                        else:
                            return "⚠ Code executed but produced no result. Please rephrase your query."
            
            # Check if we got a result
            if result is None:
                return "⚠ No result produced. Please try rephrasing your query."
            
            # Use professional formatter for all result types
            return self._format_result_professionally(result)
                
        except Exception as e:
            print(f"❌ Error executing code: {e}")
            import traceback
            traceback.print_exc()
            return f"⚠ Error processing query: {str(e)}"
    
    def get_context_used(self) -> List[str]:
        """Get the context used for the last query"""
        return self.context_used