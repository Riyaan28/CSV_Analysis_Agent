# 📊 CSV Analysis Agent - Query Examples

## Complete List of Working Queries

This document contains all the types of natural language queries that the CSV Analysis Agent can handle.

---

## 📋 Dataset Information Queries

### Basic Info

```
✅ What columns are in this dataset?
✅ How many rows and columns?
✅ How many rows does this have?
✅ How many columns does this have?
✅ What are the data types?
✅ Show me the shape
✅ What is the size of this dataset?
✅ Show me the dimensions
```

### Column Names

```
✅ What are the columns?
✅ List the columns
✅ Show columns
✅ Column names
✅ What columns are available?
```

---

## 📊 View Data Queries

### First/Head Rows

```
✅ Show first row
✅ Show first 5 rows
✅ Show me the first 10 rows
✅ Display first row
✅ Head 5 rows
✅ Top 3 rows
✅ First 2 records
✅ Show first 100 rows (shows all if dataset has fewer)
```

### Last/Tail Rows

```
✅ Show last row
✅ Show last 2 rows
✅ Show me the last 5 rows
✅ Tail 10 rows
✅ Bottom 3 rows
✅ Last 7 records
✅ End rows
✅ Show last 50 rows (shows all if dataset has fewer)
```

### View Specific Columns

```
✅ Show 3 columns
✅ Show first 4 columns
✅ Show last 2 columns
✅ Display 5 columns
✅ First 3 columns
✅ Last column
✅ Show 20 columns (shows all + note if dataset has fewer)
```

---

## 📈 Statistical Analysis Queries

### Summary Statistics

```
✅ Show statistical summary
✅ Describe the data
✅ Show me statistics
✅ Statistical analysis
✅ Give me the stats
```

### Sum/Total

```
✅ Sum of [column_name]
✅ Total of [column_name]
✅ What is the sum of performance_score?
✅ Calculate total of salary
✅ Sum of revenue
```

### Average/Mean

```
✅ Average of [column_name]
✅ Mean of [column_name]
✅ What is the average salary?
✅ Calculate mean of age
✅ Average performance_score
```

### Median

```
✅ Median of [column_name]
✅ What is the median salary?
✅ Median age
✅ Show me the median of revenue
```

### Minimum

```
✅ Min of [column_name]
✅ Minimum of [column_name]
✅ Smallest [column_name]
✅ Lowest [column_name]
✅ What is the minimum salary?
```

### Maximum

```
✅ Max of [column_name]
✅ Maximum of [column_name]
✅ Largest [column_name]
✅ Highest [column_name]
✅ What is the maximum age?
```

### Standard Deviation

```
✅ Standard deviation of [column_name]
✅ Std of [column_name]
✅ Stdev of [column_name]
✅ What is the standard deviation of salary?
```

---

## 🔍 Column Analysis Queries

### Unique Values

```
✅ Unique values in [column_name]
✅ What are the unique values in department?
✅ Show unique [column_name]
✅ How many unique values in gender?
```

### Distribution/Frequency

```
✅ Distribution of [column_name]
✅ Frequency of [column_name]
✅ Show me the distribution of department
✅ Value counts in [column_name]
```

### Count Specific Values

```
✅ How many [value] in [column_name]?
✅ Count of [value] in [column_name]
✅ How many males in gender?
✅ Count of engineers in department
✅ Number of active in status
```

---

## ❓ Missing Values Queries

### All Columns

```
✅ Missing values
✅ Null values
✅ Show missing values
✅ How many missing values?
✅ Check for null values
✅ Empty values
✅ Show me the missing data
```

### Specific Column

```
✅ Missing values in [column_name]
✅ Null values in [column_name]
✅ How many missing values in salary?
✅ Check null values in age
✅ Empty values in department
✅ Missing data in performance_score
```

**Output includes:**

- Count of missing values
- Total count
- Percentage missing

---

## 💡 Query Tips

### Column Name Matching

- The agent uses intelligent column name matching
- Works with partial names: "perf" matches "performance_score"
- Case-insensitive: "SALARY" = "salary" = "Salary"
- Uses word boundaries for accurate matching

### Number Detection

- Automatically detects numbers in your queries
- "show 5 rows" → extracts "5"
- "last 10 records" → extracts "10"
- Works with any reasonable number

### Natural Language

- Use conversational language
- "Show me" / "Display" / "What is" all work
- Can use singular or plural: "row" or "rows"
- Synonyms work: "average" = "mean", "total" = "sum"

### Smart Validation

- If you request more rows than available, shows all + note
- If you request more columns than available, shows all + note
- Clear error messages for non-numeric columns
- Helpful suggestions when column not found

---

## 🎯 Advanced Features

### Caching System

- Responses are cached for identical queries
- Semantic similarity matching (90% threshold)
- Cache indicator shows: 💾 Cached or 🔍 New
- Clear cache anytime from sidebar

### RAG Context

- Uses FAISS vector search
- Retrieves relevant context from dataset
- Shows context used in expandable section
- Improves response accuracy

### Multiple AI Models

Choose from:

- **Llama 3.2 (Latest)** - 2GB lightweight model
- **Llama 3.2 (1B)** - Ultra-fast compact version
- **Llama 2 (Latest)** - 3.8GB proven model
- **Llama 2 (7B)** - Full-featured version
- **Mistral (Latest)** - High-performance alternative
- **DeepSeek R1 (7B)** - Advanced reasoning

### Feedback System

- 👍 / 👎 buttons on each response
- Analytics dashboard in sidebar
- Satisfaction rate calculation
- Export feedback to CSV

---

## 📝 Example Session

```
User: What columns are in this dataset?
Agent: Columns in the dataset:
       - employee_id
       - name
       - department
       - salary
       - age
       - performance_score
       - hire_date
       - status

User: Show first 3 rows
Agent: [Shows table with first 3 rows]

User: Sum of salary
Agent: Sum of 'salary': 450,000.00

User: Missing values in performance_score
Agent: Missing values in 'performance_score':
       - Missing: 2
       - Total: 20
       - Percentage: 10.00%

User: Show 4 columns
Agent: First 4 columns: employee_id, name, department, salary
       [Shows table with sample data]
```

---

## 🚀 Performance

- **Fast Response**: Cached queries return instantly
- **Smart Caching**: Semantic similarity matching
- **Efficient**: Direct calculations for common queries
- **Scalable**: Handles datasets with thousands of rows

---

## 📚 Resources

- **README.md** - Full project documentation
- **VERIFICATION.md** - Assignment compliance checklist
- **QUICKSTART.md** - 5-minute setup guide
- **This file** - Complete query reference

---

**Need Help?** The agent provides helpful error messages and suggestions when queries aren't understood!

**Version:** 1.0.0  
**Last Updated:** November 4, 2025
