# Connecting to LLMs

??? info "🤖 AI Summary"

    Integration options by difficulty: **Easy** - Claude Desktop (config JSON), Claude Code CLI (.mcp.json), FastMCP Client (Python). **Medium** - LangChain, LangGraph, CrewAI, AutoGen, MCP SDK. **Hard** - Anthropic API, OpenAI API (manual tool loop). For quick chat → Claude Desktop. For Python apps → FastMCP/LangChain. For multi-step agents → LangGraph. For multi-agent → CrewAI.

This MCP server can connect to any LLM that supports the Model Context Protocol or tool calling.

## Feature Support by Client

Different clients support different MCP features. **Coaching Analysis** requires MCP Sampling support.

| Client | Tools | Resources | Sampling | Coaching Analysis |
|--------|:-----:|:---------:|:--------:|:-----------------:|
| **Claude Desktop** | ✅ | ✅ | ✅ | ✅ Full |
| **Claude Code CLI** | ✅ | ✅ | ✅ | ✅ Full |
| **Cursor** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Windsurf** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Zed** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **Continue.dev** | ✅ | ✅ | ❌ | ⚠️ Data only |
| **LangChain** | ✅ | ✅ | ⚠️ Manual | ⚠️ Requires setup |
| **OpenAI API** | ✅ | ❌ | ❌ | ⚠️ Data only |
| **Custom MCP SDK** | ✅ | ✅ | ⚠️ Optional | Depends on impl |

**Legend:**

- ✅ Full: Feature fully supported with automatic coaching
- ⚠️ Data only: Raw data returned, client LLM interprets it
- ⚠️ Manual/Requires setup: Possible but requires custom implementation

See [AI Coaching Features](../api/coaching.md) for details on coaching analysis and how to implement sampling in custom clients.

## Native MCP Support

These clients have built-in MCP support:

| Client | Setup Difficulty | Best For |
|--------|------------------|----------|
| [Claude Desktop](claude-desktop.md) | Easy | Interactive chat with tools |
| [Claude Code CLI](claude-code.md) | Easy | Development workflows |

## Agentic Frameworks

Use MCP tools with popular agent frameworks:

| Framework | Setup Difficulty | Best For |
|-----------|------------------|----------|
| [LangChain](langchain.md) | Medium | Complex agent pipelines |
| [LangGraph](langgraph.md) | Medium | Stateful multi-step agents |
| [CrewAI](crewai.md) | Medium | Multi-agent collaboration |
| [AutoGen](autogen.md) | Medium | Conversational agents |

## Direct API Integration

For custom implementations:

| Method | Setup Difficulty | Best For |
|--------|------------------|----------|
| [FastMCP Client](fastmcp.md) | Easy | Python scripts |
| [MCP SDK](mcp-sdk.md) | Medium | Custom clients |
| [Anthropic API](anthropic-api.md) | Hard | Full control |
| [OpenAI API](openai-api.md) | Hard | OpenAI models |

## Which Should I Use?

**Just want to chat with match analysis?**
→ [Claude Desktop](claude-desktop.md)

**Building a Python application?**
→ [FastMCP Client](fastmcp.md) or [LangChain](langchain.md)

**Need complex multi-step analysis?**
→ [LangGraph](langgraph.md)

**Want multiple specialized agents?**
→ [CrewAI](crewai.md)
