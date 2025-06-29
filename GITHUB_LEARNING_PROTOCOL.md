# GitHub Learning Protocol for Claude Search System

## Overview
This protocol defines how the Claude GitHub Search System learns from successful searches and updates the repository with patterns for future use.

## Architecture Flow

```
1. User Query → 2. Fetch GitHub Context → 3. Claude API Search → 4. Document Learning → 5. Update GitHub
                      ↑                                                                        ↓
                      ←─────────────────── Learning Loop ──────────────────────────────────→
```

## Learning Trigger Criteria

### When to Document a Search as "Successful"
A search is considered successful and worth documenting when:

- **Result Count**: Found 3+ relevant results
- **Specificity**: Results contain exact episode references with timestamps  
- **YouTube Links**: Generated working YouTube timestamp links
- **Pattern Recognition**: Used specific SQL patterns or search strategies
- **Novel Approach**: Discovered new search methodology

### What NOT to Document
- Searches with 0-2 results
- Generic fallback searches
- Duplicate patterns already documented
- Error states or failed queries

## Learning Document Structure

### Filename Convention
```
search_learning_YYYYMMDD_HHMM_[query_slug].md
```

### Template Structure
```markdown
# Search Learning: [Original Query]

**Generated**: [ISO timestamp]
**Results Found**: [count]
**Success Level**: [High/Medium/Low]

## Query Analysis
**Original Query**: "[exact user query]"
**Query Type**: [biographical/academic/relationships/etc.]
**Lewis Period**: [childhood/WWI/oxford_student/early_academic]

## Successful Search Patterns

### Primary Strategy
- **Approach**: [specific search strategy used]
- **Key Terms**: [terms that produced results]
- **SQL Pattern**: [working SQL query pattern]

### SQL Patterns Used
[List of SQL queries with descriptions and result counts]

### Episode Targeting
- **Episodes Found**: [list of episodes with relevant content]
- **Time Periods**: [chronological range]
- **Content Themes**: [what types of content were found]

## Key Results Found
[Top 5 results with episode, timestamp, YouTube link, quote]

## Pattern Analysis

### What Worked
- [Specific search techniques that succeeded]
- [Term combinations that found content]
- [Database approaches that worked]

### What Failed Initially
- [Approaches tried that didn't work]
- [Terms that returned 0 results]
- [Why initial strategy needed refinement]

### Search Evolution
- [How the search strategy evolved]
- [Refinements made during the process]
- [Final successful approach]

## Lessons for Future Searches

### Recommended Patterns
- [SQL patterns to reuse for similar queries]
- [Search term expansions that work]
- [Episode ranges to target]

### Terminology Discoveries
- [New Lewis-specific vocabulary found]
- [Synonym patterns that work]
- [Phrase variations that match]

### Technical Insights
- [Database query optimizations]
- [Timestamp conversion patterns]
- [YouTube link construction notes]

## Replication Instructions

### For Similar Queries
1. [Step-by-step process to replicate success]
2. [Specific terms to try first]
3. [Fallback strategies if initial approach fails]

### Integration with Existing Patterns
- [How this connects to previous learning]
- [Patterns that reinforce existing knowledge]
- [New insights that update previous understanding]
```

## GitHub Update Process

### Automatic Documentation
The system automatically:

1. **Analyzes Search Success** - Evaluates result quality and approach effectiveness
2. **Generates Learning Document** - Creates structured documentation following template
3. **Commits to Repository** - Pushes to `/search_learnings/` directory with descriptive commit message
4. **Updates Context Package** - Ensures next search includes new patterns

### Manual Review Process
Periodically review accumulated learning documents to:

- **Consolidate Patterns** - Merge similar approaches into comprehensive guides
- **Update Core Search Logic** - Integrate successful patterns into `intelligent_claude_search.py`
- **Refine Context Package** - Optimize what gets included in GitHub context
- **Archive Superseded Learning** - Move outdated patterns to archive

## Context Package Evolution

### Dynamic Context Building
The GitHub context package evolves by:

- **Adding New Learning Docs** - Include recent successful search patterns
- **Updating Search Examples** - Reference working SQL patterns from learning
- **Expanding Term Libraries** - Add discovered Lewis vocabulary
- **Refining Episode Mappings** - Improve episode-to-content targeting

### Version Control
Each context package includes:
- **Commit SHA** - Track which version of learning was used
- **File Counts** - Monitor growth of learning documents
- **Success Metrics** - Track improvement in search quality over time

## Quality Assurance

### Learning Document Review
Before committing learning documents:

- **Verify SQL Syntax** - Ensure patterns are valid and reusable
- **Validate YouTube Links** - Confirm timestamp links work correctly
- **Check Episode References** - Verify episode numbers and titles
- **Review Pattern Logic** - Ensure search strategy is clearly documented

### Pattern Validation
Periodically test documented patterns:

- **Replay Successful Searches** - Verify patterns still work
- **Test Pattern Variations** - Ensure robustness across similar queries
- **Measure Improvement** - Track search success rates over time
- **Update Outdated Patterns** - Refresh patterns that stop working

## Integration with Claude API

### Context Delivery
The GitHub context package provides Claude with:

- **Complete Project State** - All files, patterns, and learning
- **Search Methodology** - Documented successful approaches
- **Lewis Knowledge Base** - Accumulated biographical insights
- **Technical Patterns** - SQL templates and URL construction

### Learning Feedback Loop
Claude API responses are analyzed for:

- **New Pattern Discovery** - Novel search approaches worth documenting
- **Pattern Refinement** - Improvements to existing methodologies
- **Failure Analysis** - Understanding why certain approaches don't work
- **Success Replication** - Ensuring successful patterns are preserved

## Monitoring and Metrics

### Success Tracking
Monitor search system improvement through:

- **Result Quality** - Average relevance of search results
- **Response Time** - Speed of finding relevant content
- **Pattern Reuse** - How often learned patterns get applied
- **User Satisfaction** - Quality of final search results

### Learning Velocity
Track learning system effectiveness:

- **Documents Generated** - Number of successful patterns documented
- **Pattern Application** - How often previous learning helps new searches
- **Knowledge Accumulation** - Growth in Lewis-specific search capabilities
- **Search Evolution** - Improvement in search sophistication over time

## Maintenance Protocol

### Regular Reviews
- **Weekly**: Review new learning documents for quality
- **Monthly**: Consolidate similar patterns and update core search logic
- **Quarterly**: Archive outdated patterns and optimize context package
- **Annually**: Comprehensive review of search system evolution

### Repository Hygiene
- **Organize Learning Documents** - Maintain clear directory structure
- **Update Documentation** - Keep protocols current with system evolution
- **Archive Historical Patterns** - Preserve evolution history
- **Optimize Context Size** - Balance completeness with API efficiency