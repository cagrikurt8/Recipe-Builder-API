# Recipe-Builder-API
A Flask API Application

A Flask API application in which you add, delete, update and get recipes from a database with http requests POST, DELETE, PUT and GET. You can use Postman for the http requests. The programs runs on the localhost.

POST method URL => /api/recipe/new  this request is sent with a json body. The sent json will be recorded to the database with an auto incremented id. It returns the id of the
                                    recipe in the format of json object.

GET method URL with id => /api/recipe/{recipe_id}   where recipe_id can be 1, 2, 3 and so on in the database. If the requested recipe with the specified id exists, it is returned.                                                     Otherwise, the application return status code 404(Not found).

GET method URL with args => /api/recipe?ingredients={ingredient1}|{ingredient2}|...|{ingredientN}   where ingredients can be water, ginger etc. To get a recipe, the entered                                   ingredients should cover all the ingredients list of any recipe or a recipe with ingredients that is a subset of the entered ingredients should                                     exist. Also, after ingredients you can set 'max_directions' argument to get recipes that has less than or equal to {max_directions} number of                                       directions. The final form of this URL: 
                            /api/recipe?ingredients={ingredient1}|{ingredient2}|...|{ingredientN}&max_directions={max_direction}.

DELETE method URL => /api/recipe/{recipe_id}  The requested recipe will be deleted from the database if a recipe exists with the specified id. Otherwise, it returns status code                                                 404.

PUT method URL => /api/recipe/{recipe_id}   This request is sent with a json body, the json stores the new recipe in json format. If a recipe exists with the given id, it is                                                   replaced with the json comes with the request.
