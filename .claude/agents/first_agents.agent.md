---
name: first_agents
description: Describe what this custom agent does and when to use it.
tools: Read, Grep, Glob, Bash # specify the tools this agent can use. If not set, all enabled tools are allowed.
---

<!-- Tip: Use /create-agent in chat to generate content with agent assistance -->

1. If python coding is involved, check that the python environment in $HOME/repos/venv/bin/activate  has been activated
2. Check that any zsh shell has access to /bin and /usr/bin and if not add them via this command:

PATH=$PATH:/bin:/usr/bin

3. Any python code needed to complete the task should be placed in separate script files. 
4. If jupyter notebooks are used, modify the code in their notebook cells and add markdown cells explaining them.
5. For any task, ask if test files should also be created

