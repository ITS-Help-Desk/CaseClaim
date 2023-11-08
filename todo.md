# TODO

1. Refactor all commands that generate generic graphs (leadstats, ...) to accept making changes only using SQL connector
    - More Specfically:
        - Extract all graphs into helper methods that can function off of only a database connection and strs
        - Rewrite bot to extract types and classes related more to the db than the bot to their own directory
        - tldr: Partially convert from oop pattern to composition pattern
2. On a get request, generate a fresh graph and render it out to the user via templating
    - Implement a control panel that will allow user to select parameters to generate graphs
    - Use the methods extracted in step 1 to integrate all graph commands into both the bot and the website
4. Add style
5. Fix issue where bot command line output is not captured by `get_buffered_inputs()`
