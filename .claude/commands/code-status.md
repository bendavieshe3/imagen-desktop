Generate information about the codebase and summarise the results to the user, following these steps:
1. Check that all local changes have been committed
2. Report if the local repo is ahead or before of the remote github branch
3. Check how many github issues are currently open
4. Check how many TODOs are defined in ./TODO.md
5. Check if these TODOs are not captured as github issues, and if so, ask the user if they want to add them. Add them if the user agrees.
6. List the number of tests defined
7. List the current coverage metric for the tests, along with when the coverage was generated. 
8. Perform a quick assessment about the health of the code project and provide it to the user. 

