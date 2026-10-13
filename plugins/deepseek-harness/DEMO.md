# Keyless Integration Demo

This is a prompt/tool integration demonstration, not a model-generated manuscript.
Run `pnpm test` from the repository root with Python 3.9+ available.

The official Cordis test mounts SystemPrompt, ToolRuntime, and this plugin, then
discovers `mcp__writing-integration__compile_generation_prompt`, calls it with
an academic-writing task, checks that the returned instructions include the
generation-quality protocol, and unloads the plugin. Both tools and prompt section
are removed. The protocol test additionally uses a real Python stdio process to:

1. Negotiate MCP and list tools.
2. Compile fiction, academic-paper, and formal-document instructions.
3. Supply a source file containing an observed six-hour device test.
4. Confirm that the evidence appears in the self-media writing prompt.
5. Reject `../outside.md` as a source path.
6. Compare “The effect may be 20%.” with “The effect is 20%.” and receive
   `needs-review`, even though the number remains unchanged.

The test places a fake `humanwriting.py` in the workspace; isolated startup still
loads the bundled core. These checks require no DSH account or LLM API key.
Human/native-speaker evaluation of the prose is a separate activity.
