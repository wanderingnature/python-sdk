# Changes to Implement Prompt Arguments accepting dict[str,Any]

# Proposal: Enhanced Prompt Arguments in Model Context Protocol

## Background

The Model Context Protocol (MCP) currently defines two main mechanisms for parameter passing:

1. Tools: Support typed arguments with JSON Schema validation
2. Prompts: Support string-only arguments without schema validation

This creates an inconsistency in the specification, particularly given the security and validation requirements stated for prompts:

- Servers SHOULD validate prompt arguments before processing
- Implementations MUST carefully validate inputs/outputs to prevent injection attacks
- Both parties SHOULD respect capability negotiation

It is overly complex and likely not backward compatible to change prompt arguments to use a schema as tools do. However, it is possible to make a small compatible change to allow more complex inputs and enable reasonable model validation with a simple backwards compatible change. That change is specifically to allow the less strict dict[str, Any] for arguments rather than the currently strict dict[str, str]. As Any includes str this change is fully backwards compatible. There are limitations to this change as far as passing argument schema to the client (you cannot directly do that), but with some 'rules' regarding how to define function arguments it is possible to build clients which can discover the arguments model of a server prompt at runtime. 

## Example

You can check the changes with various new examples using the provided example client, prompt_complex_data.py

```text
	examples/fastmcp/echo_prompt.py
	examples/fastmcp/echo_prompt_args.py
	examples/fastmcp/edge_case_prompts.py
	examples/fastmcp/prompt_complex_data.py
```


## Changed files
```text
	modified:   pyproject.toml
	modified:   src/mcp/client/session.py
	modified:   src/mcp/server/fastmcp/prompts/base.py
	modified:   src/mcp/server/fastmcp/server.py
	modified:   src/mcp/server/lowlevel/server.py
	modified:   src/mcp/types.py
```

### pyproject.toml
```text
git diff  pyproject.toml
diff --git a/pyproject.toml b/pyproject.toml
index 31a5494..9237f59 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -25,7 +25,7 @@ dependencies = [
     "anyio>=4.5",
     "httpx>=0.27",
     "httpx-sse>=0.4",
-    "pydantic>=2.10.1,<3.0.0",
+    "pydantic[email,mail]>=2.10.1,<3.0.0",
     "starlette>=0.27",
     "sse-starlette>=1.6.1",
     "pydantic-settings>=2.6.1",
```

### src/mcp/client/session.py

```text
git diff  src/mcp/client/session.py
diff --git a/src/mcp/client/session.py b/src/mcp/client/session.py
index 27ca74d..87f240e 100644
--- a/src/mcp/client/session.py
+++ b/src/mcp/client/session.py
@@ -1,4 +1,5 @@
 from datetime import timedelta
+from typing import Any
 
 from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
 from pydantic import AnyUrl
@@ -182,7 +183,7 @@ class ClientSession(
         )
 
     async def get_prompt(
-        self, name: str, arguments: dict[str, str] | None = None
+        self, name: str, arguments: dict[str, Any] | None = None
     ) -> types.GetPromptResult:
         """Send a prompts/get request."""
         return await self.send_request(
```

### src/mcp/server/fastmcp/prompts/base.py

```text
git diff  src/mcp/server/fastmcp/prompts/base.py
diff --git a/src/mcp/server/fastmcp/prompts/base.py b/src/mcp/server/fastmcp/prompts/base.py
index 0df3d2f..e956928 100644
--- a/src/mcp/server/fastmcp/prompts/base.py
+++ b/src/mcp/server/fastmcp/prompts/base.py
@@ -61,6 +61,9 @@ class PromptArgument(BaseModel):
     required: bool = Field(
         default=False, description="Whether the argument is required"
     )
+    type: str | None = Field(
+        default=None, description="Type of the argument"
+    )
 
 
 class Prompt(BaseModel):
@@ -108,6 +111,7 @@ class Prompt(BaseModel):
                         name=param_name,
                         description=param.get("description"),
                         required=required,
+                        type=param.get("type")  # hotfix
                     )
                 )
```

### src/mcp/server/fastmcp/server.py

```text
diff --git a/src/mcp/server/fastmcp/prompts/base.py b/src/mcp/server/fastmcp/prompts/base.py
index 0df3d2f..e956928 100644
--- a/src/mcp/server/fastmcp/prompts/base.py
+++ b/src/mcp/server/fastmcp/prompts/base.py
@@ -61,6 +61,9 @@ class PromptArgument(BaseModel):
     required: bool = Field(
         default=False, description="Whether the argument is required"
     )
+    type: str | None = Field(
+        default=None, description="Type of the argument"
+    )
 
 
 class Prompt(BaseModel):
@@ -108,6 +111,7 @@ class Prompt(BaseModel):
                         name=param_name,
                         description=param.get("description"),
                         required=required,
+                        type=param.get("type")  # hotfix
                     )
                 )
 
(fullpygis) deepnpisgah@MacPro2013 python-sdk % git diff  src/mcp/server/fastmcp/server.py      
diff --git a/src/mcp/server/fastmcp/server.py b/src/mcp/server/fastmcp/server.py
index 571c7c2..b9a6822 100644
--- a/src/mcp/server/fastmcp/server.py
+++ b/src/mcp/server/fastmcp/server.py
@@ -471,6 +471,7 @@ class FastMCP:
                         name=arg.name,
                         description=arg.description,
                         required=arg.required,
+                        type=arg.type  # add to get type on client
                     )
                     for arg in (prompt.arguments or [])
                 ],
```

### src/mcp/server/lowlevel/server.py

```text
diff --git a/src/mcp/server/lowlevel/server.py b/src/mcp/server/lowlevel/server.py
index 32ea279..69ce59f 100644
--- a/src/mcp/server/lowlevel/server.py
+++ b/src/mcp/server/lowlevel/server.py
@@ -207,7 +207,7 @@ class Server:
     def get_prompt(self):
         def decorator(
             func: Callable[
-                [str, dict[str, str] | None], Awaitable[types.GetPromptResult]
+                [str, dict[str, Any] | None], Awaitable[types.GetPromptResult]
             ],
         ):
             logger.debug("Registering handler for GetPromptRequest")
```


### src/mcp/types.py

diff --git a/src/mcp/types.py b/src/mcp/types.py
index 4e1628c..2030b7f 100644
--- a/src/mcp/types.py
+++ b/src/mcp/types.py
@@ -534,6 +534,8 @@ class PromptArgument(BaseModel):
     """A human-readable description of the argument."""
     required: bool | None = None
     """Whether this argument must be provided."""
+    type: str | None = None
+    """Type of the argument."""
     model_config = ConfigDict(extra="allow")
 
 
@@ -560,7 +562,7 @@ class GetPromptRequestParams(RequestParams):
 
     name: str
     """The name of the prompt or prompt template."""
-    arguments: dict[str, str] | None = None
+    arguments: dict[str, Any] | None = None
     """Arguments to use for templating the prompt."""
     model_config = ConfigDict(extra="allow")








