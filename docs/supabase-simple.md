# Simplified Supabase Integration

This provides a much simpler alternative to the complex Postgres connection handling. Instead of managing raw database connections, migrations, and IPv4 rewrites, we use the Supabase Python client directly.

## Quick Setup

1. **Set environment variables:**
   ```bash
   export SUPABASE_URL="https://your-project.supabase.co"
   export SUPABASE_ANON_KEY="your-anon-key"
   ```

2. **Create tables in Supabase:** (via SQL Editor or dashboard)
   ```sql
   -- Articles table
   CREATE TABLE articles (
     id SERIAL PRIMARY KEY,
     title TEXT,
     url TEXT UNIQUE,
     content TEXT,
     author TEXT,
     published_date TIMESTAMPTZ,
     source TEXT,
     publisher TEXT,
     tags TEXT[],
     extracted_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Watermarks table
   CREATE TABLE watermarks (
     source_key TEXT PRIMARY KEY,
     last_processed TIMESTAMPTZ
   );

   -- Processing logs table
   CREATE TABLE processing_logs (
     id SERIAL PRIMARY KEY,
     source_key TEXT,
     status TEXT,
     message TEXT,
     timestamp TIMESTAMPTZ DEFAULT NOW()
   );
   ```

3. **Run the simplified pipeline:**
   ```bash
   # Local SQLite (existing behavior)
   python -m src.cli simple-pipeline --config config/feeds.yaml

   # With Supabase
   python -m src.cli simple-pipeline --config config/feeds.yaml --supabase
   ```

## Enhanced NFL.com Integration

The pipeline now includes advanced NFL.com processing with:

### ✅ **Full Content Extraction**
- Extracts complete article text, not just titles
- Intelligent content cleaning and formatting
- Author and publish date extraction

### ✅ **Smart Filtering**
- Only processes articles from the last 7 days (configurable)
- URL pattern-based date detection
- Configurable article limits (default: 30 per run)

### ✅ **Dynamic URL Templates**
- Automatically expands `{YYYY}/{MM}` patterns
- Current example: `https://www.nfl.com/sitemap/html/articles/2025/09`
- No manual URL updates needed

### 📊 **Results**
```
✅ NFL.com: 30 articles (from 88 available in sitemap)
   - Full article content extracted
   - Only recent articles (last 7 days)
   - Proper titles, authors, and publish dates
```

### ⚙️ **Configuration**
```yaml
- name: NFL.com - Articles Monthly Sitemap
  type: sitemap
  url_template: https://www.nfl.com/sitemap/html/articles/{YYYY}/{MM}
  publisher: NFL.com
  max_articles: 30     # Process up to 30 recent articles
  days_back: 7         # Only articles from last 7 days
  extract_content: true # Extract full article content
```

## Benefits

- ✅ **No complex Postgres connection handling**
- ✅ **No IPv4/IPv6 networking issues**
- ✅ **No Alembic migrations needed**
- ✅ **Uses Supabase's built-in auth and APIs**
- ✅ **Simpler error handling**
- ✅ **Can still use local SQLite for development**

## GitHub Actions

Use the new simplified workflow:

```yaml
# .github/workflows/simple-supabase.yml
```

Set these GitHub secrets:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anon key

## Comparison

| Approach | Complexity | Setup | Error Handling |
|----------|------------|-------|----------------|
| **Complex Postgres** | High | Many env vars, migrations, IPv4 fixes | Complex connection errors |
| **Simple Supabase** | Low | 2 env vars, create tables | Simple HTTP errors |

The simplified approach eliminates all the networking and connection complexity while providing the same functionality.
