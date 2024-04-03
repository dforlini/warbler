# questions from step 7 

1. How is the logged in user being kept track of?
## logged in user is being tracked by flask's session mechinism 
## session key named curr_user_key, when user logs in via do_login
## id is stored in the session

2. What is Flask’s g object?
## special obj provided by flask that is unique for ea request.
## used to store data during app context, which can be assessed by different parts of the app during that request
## g stands for global, but not globally accessable across different requests
## global in the context of a single request

3. What is the purpose of add_user_to_g ?
## function designed to retrieve the currently logged in user from the datatbase and attach it to flasks g object

4. What does @app.before_request mean?
## a decorator used to register a function that runs before each request is processed by a flask app. its executed before the view function corresponding to the request. 

