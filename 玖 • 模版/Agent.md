<%*
const desc = await tp.system.prompt("description")
const provider = await tp.system.prompt("provider")
const model = await tp.system.prompt("model")
const tools = await tp.system.prompt("tools")
const temp = await tp.system.prompt("temperature", "0.7")
const perm = await tp.system.prompt("permission")
const top_p = await tp.system.prompt("top_p", "0.9")

tR += `---
description: ${desc}
provider: ${provider}
model: ${model}
tools: ${tools}
temperature: ${temp}
permission: ${perm}
top_p: ${top_p}
---
%% Who are you%%
%%What to do%%
%%How to complete the task%%
%%What tools can be used%%
%%What behavior is absolutely prohibited%%
`
%>
<% tp.file.cursor() %>