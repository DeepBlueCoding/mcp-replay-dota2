# Connecting to LLMs

??? info "🤖 AI Summary"

    Integration options by difficulty: **Easy** - Claude Desktop (config JSON), Claude Code CLI (.mcp.json), FastMCP Client (Python). **Medium** - LangChain, LangGraph, CrewAI, AutoGen, MCP SDK. **Hard** - Anthropic API, OpenAI API (manual tool loop). For quick chat → Claude Desktop. For Python apps → FastMCP/LangChain. For multi-step agents → LangGraph. For multi-agent → CrewAI.

This MCP server can connect to any LLM that supports the Model Context Protocol or tool calling.

## Feature Support by Client

Different MCP clients support different features:

| Client | Tools | Resources | Prompts | Notes |
|--------|:-----:|:---------:|:-------:|-------|
| **Claude Desktop** | ✅ | ✅ | ❌ | No prompts support |
| **Claude Code CLI** | ✅ | ✅ | ✅ | Resources via `@`, prompts via `/mcp__` |
| **Cursor** | ✅ | ❌ | ❌ | Tools only |
| **Windsurf** | ✅ | ❌ | ❌ | Tools only |
| **Zed** | ✅ | ✅ | ❌ | No prompts |
| **Continue.dev** | ✅ | ✅ | ❌ | No prompts |
| **VS Code + Copilot** | ✅ | ✅ | ⚠️ | Partial support |
| **LangChain** | ✅ | ✅ | ⚠️ | Manual prompt loading |
| **OpenAI API** | ✅ | ❌ | ❌ | Tools via function calling |

**Legend:**

- ✅ Supported
- ⚠️ Partial/manual implementation
- ❌ Not supported

See [Prompts](../api/prompts.md) for available coaching prompts.

Sources: [Claude Code MCP Docs](https://code.claude.com/docs/en/mcp), [MCP Sampling Status](https://modelcontextprotocol.info/docs/concepts/sampling/)

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
