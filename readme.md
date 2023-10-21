# PyChess


## What is PyChess?

PyChess is a website prototype where you can go to play chess online with your friends.  
After registering for an account you can start a game locally, with you and a friend sitting at the same computer,  
or over the network by sharing your "Room Code" with your friend, where they can play from their own computer.  
PyChess also includes the ability to review previously completed games turn-by-turn; and the ability to spectate games  
currently in progress by other users; provided you have the room code.


## Distictiveness and Complexity  

I knew from the start of this project that I wanted to build a site around some kind of in-browser game.  
With the previous CS50w projects being a Wiki, an eCommerce site, an email client, and a social network;   
I belive a semi-realtime interactive game meets the distinctiveness requirement.  

From a complexity standpoint; I started the project with a few design goals in mind.  
I wanted the site based around a game that could be played in-browser.
I wanted the game to have online multiplayer functionality.
I wanted to use as few frameworks or libraries as possible, with the exception of those required by the project guidelines.  

My decision to not use any external libraries was simply a personal goal; I just wanted to see if I could make  
a functioning game and a nice looking webpage without using tools like React or Bootstrap. Ultimately; this led to me   
spending more time on the site CSS than any other aspect of the project; which may have been a mistake, but I'm pleased with the results  
and I feel as though I've learned a lot about the quirks of CSS by taking this approach. 

My desire for an online multiplayer experience, combined with the decision not to use any external libraries, limited the type  
of game I'd be able to make. It needed to be turn based; and I needed to be able to succintly decribe and store the state of the game  
at any point as a database entry. It was also preferable that the rules to the game be relatively simple, just for the sake of time.  
These requirements led me to Chess; but as I discovered, the rules for Chess are deceptively complex, and it ended up taking me much  
longer to code the game engine than I would have liked.  

The game engine itself is written partly in raw Python and partly in raw JavaScript. These parts communicate with each other  
through API requests, implemented as Django methods. The idea is that the Python back end is in charge of the game logic and maintaining  
the current state of the game. The JavaScript front end is in charge of user Input and Output. Any time the state of the game changes,  
the back end will store the change in the database; where either user can retrive and recreate the game state; thus keeping both users in sync.  

An overview of the control flow for one turn goes something like this:
- The frontend makes a fetch request to the `gameState` API route.  
- Django makes a call to the Chess Engine to generate the current board state as a Python Dictionary object.  
    - The chess engine accomplishes this by retrieving a list of all the moves that have been made in the current game from the database.
- The dictionary is converted to a JSON object and returned to the front end. 
- The frontend draws the board and pieces on screen; using the JSON state to determine where each piece belongs.
- User 1 clicks a piece on the board
- The JS front end makes a fetch request to the `check` API route; passing some info about the clicked piece.
- The backend generates and returns a list of possible coordinates where the piece can move.
- The frontend finds and highlights the board cells in the list.
- User 1 clicks a highlighted cell.
- The frontend makes a fetch request to the `submitMove` API route; passing in the desired coordinates to move.
- The backend will verify that the move is valid. If so, it will create and store a new `Move` object to the database.
- An updated board state is generated which is then passed back to the frontend.
- The front end will draw the new board; and the turn will end for User 1.

Meanwhile for User 2; the front end will poll the `gameState` API periodically to check for changes. 
If the current stored game state is different from the state returned by the server; then it's safe to assume  
the opposing user has made their move. The new board is displayed; and the outline above repeats from the top; this time  
listening for input from User 2; while User 1 polls for changes in the game state.  


## Code Overview

### Styles.css

The styling and CSS for the site took longer than any other individual part of this project. While I had a bit of  
JavaScript and Python experience before starting this course; the HTML and CSS were nearly brand new to me. As such   
there were parts of the CSS that I found to be finnicky and counterintuitive, but choosing to write this project without  
the use of libraries such as bootstrap; I feel I now have a much better grasp of CSS as a whole than before.  

Overall; the site is made almost entirely of nested flexboxes. The top level div, called `screen` covers the entire screen;  
and is displayed as a flex. Its child components are `header`, `content`, and `footer`; arranged in a column. These sections can be  
seen on the page as being divided by screen-length horizontal bars.  

The `header` is again divided into three sections arranged in a column: `mainHeader`, `subHeader`, and `navBar`. This is where  
the large "pyChess" lives at the top of the page; and the "Logged in as: " section immediately under it. The navBar is again a flexbox  
arranged horizontally, and holds each of the `navLink` items to navigate the site. The `navLink` items are simple links with borders on  
the left and right side to aestheically separate themselves from each other. Every `<a>` tag on the site is stylized with a golden-yellow  
color and will highlight with a white background and blue text when the pointer hovers over them. 

The `footer` div displays at the bottom of the screen and is just a simple container to display "a CS50 project by Chris Goins"

The `content` div is the large middle section; and is the main part of the page that will change to display different content as the user  
navigates around the site. I'll go into more detail in the next section; but aside from the game board itself; which is displayed  
as a `grid`, every container on the site is some sort of `flexbox`. This allows me to keep the content centered on the page while  
still maintaining a fairly rigid structure for the different elements.  

The final CSS note for the site is the use of `@media` tags to dictate how the page should respond on smaller screens.  
There is one main `@media` tag in the `styles.css` file which changes the size of the fonts used in the main `header`, `content`,   
and `footer` divs to make the text and links easier to read and click on small screens; such as a smartphone or tablet.  
Each individual page also has its own `<style>` tag with a media query where needed. These queries give instructions on how to  
lay the items out based on the windows aspect ratio. This approach was taken with primarily smartphones in mind, since typically  
the screen would be taller than it is wide. I found this approach works especially well since the page will respond if the user  
rotates their phone screen horizontally; or if a desktop user resizes their browser window to be smaller.  


### HTML

The HTML for the site is split into 11 different files:
- `layout.html` contains the `header`, `content`, and `footer` divs detailed in the previous section. Every other page displays its contents within this `content` div.
- `login.html` is, as the name implies, the login page. A simple form for the users name & password. This is the default landing page for a user who is not already logged in.
- `register.html` is the registration page for a user to create an account. A simple form asking for a username, email, password, and password confirmation.
- `index.html` is the sites homepage. From this page a logged in user can see a count of games they have won or lost, as well as a list of all active games they're participating in.
    - This is the default landing page for a logged in user. A user who is not logged in will be redirected to the login page.
- `play.html` allows the user to start a new game or join an existing game. Clicking the "Join Network Game" link will prompt the user for the room code of the game they'd like to join.
- `review.html` displays a list of finished games the user has participated in. Clicking a game will direct the user to a page where they may watch the past game play out step-by-step.
- `spectate.html` prompts the user for a room code, where they can then watch a game between 2 other users without themselves participating.
    - This was originally intended to be a social feature where friends could get together to play and watch each other play. The original idea included a type of text chat where spectators  
        could talk to each other, but in the interest of time the chat feature has been omitted for now.

The final four pages are `localGame.html`, `networkGame.html`, `reviewGame.html`, and `spectateGame.html`. These are the four pages where  
the board is drawn and the game actually takes place. Functionally, the four pages are very similar to each other. The HTML just lays out a few  
mostly-empty `<div>` items and a large `<script>` item; where the JavaScript handles the bulk of the interactivity. 

- `localGame.html` is for playing a local game; where both players can take turns and play from the same physical device.
- `networkGame.html` is for playing a game where each player is on a different physical device. A 'room code' is provided which can be shared to a friend.  
    This room code allows both players to see and interact with the same game board from different devices.
- `reviewGame.html` allows a user to review a previously completed game. The first obvious difference is the presence of the rewind, stop, play, and fast-forward buttons  
    at the bottom of the information panel. These buttons allow the user to watch the game as it originally played out; pause the playback, or step through it one turn at  
    a time either forwards or in reverse.
- `spectateGame.html` allows a user to watch an in progress game being played by two other players. In this game mode, the board and pieces are rendered the same as the  
    other three game modes, but no input is taken from the spectating player.

More detail on these different game modes will be provided in the `JavaScript` section.


### Database Models

This section will quickly outline the database models used in this project, as seen in `models.py`.
The three main classes here are:
-`User`
-`Game`
-`Move`

The `User` model is handled mostly by Django itself, and is used for authenticating login credentials; similar to every other CS50w project thus far.

The `Game` model is a description of a specific game that has taken place, and contains a bit of info about the game in question:
- `roomCode` contains a 6-digit alphanumeric identifier that players can use to join each others games when playing online.
- `player1` is a reference to the `User` model and contains the username of the player who plays as the light-colored pieces.
- `player2` is a reference to the `User` model and contains the username of the player who plays as the dark-colored pieces.
- `isActive` is a boolean value used to determine if the game is finished or if it's still in progress. `True` = in progress; `False` = game is finished.
- `winner` is a reference to the `User` model and contains the username of the player who won this particular game. It is null by default.
    - If `isActive` is `False`; the outcome of the game can be determined by this field. Naturally if a checkmate was achieved during the game,  
        the winners name (either `player1` or `player2`) will be recorded here. It can be extrapolated that player who is not listed here lost the game,  
        and the stats can be recorded accordingly. If `isActive` is `False` and this field is null, the game ended in either a draw or a Stalemate.

The `Game` model also contains an implicit `id` field.

The `Move` model is a record of individual moves made.  
Each record is associated with a specific `Game` item; and is stored in the `GameID` field.
Each record also contains the following:
- `moveNumber` is the turn number on which this specific move took place.
- `pieceID` is the specific piece on the board that this move refers to.
- `rankFile` is the specific position on the board the piece is to move to.
    - This is stored as a two-character alphanumeric string in conventional Chess notation. I.e., "A4" or "F7" to refer to specific board tiles.


This method of tracking and storing moves made during all of the different games on the site is almost certainly not the most optimal way of storing this information.
I noticed while testing the game that it didn't take long to end up with hundreds or even thousands of `Move` entries in the database. It seems that in a live site with  
even a handful of players this could quickly spiral into an enormous amount of entries, and the frequency with which these entries are retrieved from the database  
could potenially result in performace issues.
This project was intended to be more of a proof-of-concept; so this model was left as is. If this site were to ever go live and become accessible to the public; I would  
spend a fair amount of time re-thinking and optimizing how this information is stored and transmitted.  


### Django/views.py

This section will go into further detail on the implementation of each route on the site, in the order the routes are defined in the `views.py` file.

`index` begins by checking if the user is logged in. If not; they're redirected to the `loginView` route.
Makes a few queries to the `Game` model; collecting a list of active games where the User is listed as Player1, Player2, or both Player1 and Player2.
The games where the user is listed as both players are local games; and are added to a list. (Called `localGames`)
The games where the user is listed as only one or the other are network games, and are added to a seperate list. (Called `activeNetworkGames`)

A dictionary object is created called `completedGames` which will contain the users Wins, Losses, and Draws.

Then another set of queries are made to retrieve a list of games the user has been associated with where `isActive = False`.
This querySet is stored in `netGameQuery`. 
The query is first made for `user = player1`. It is then iterated through in a `For` loop, where the `Winner` field is checked for each entry.  
If `winner` field is empty; the game is a draw and `completedGames[draws]` is incremented.
If the user is listed as the `winner`, the game was won and `completedGames[wins]` is incremented.
If the `winner` field is anything else, the game was lost and `completedGames[losses]` is incremented.
Then the same process is done for `user = player2`.

Finally, the `index.html` page is rendered, passing in the `localGames` list, the `activeNetworkGames` list, and the `completedGames` dictionary for the page to display.  
Stats for completed local games are not counted since the user is listed as both `player1` and `player2`.


`loginView`, `logoutView`, and `register` are fairly self-explanatory. These routes use the same method as every CS50w project leading up to this point.  
- `loginView` takes the username and password as a `POST` request and calls Django's `authenticate` function; re-rendering the page with an error if the user could not be authenticated.  
- `logoutView` logs the user out and redirects to the `loginView` route.
- `register` takes the users info via `POST` request and attempts to create a new `User` record. If the attempt fails, the page is re-rendered with an error.  
    Otherwise, the account is created, the user is logged in, and redirected to the `index` route.


`play` 
The user can access this route from the "Play" tab on the navbar. In the event of a typical `GET` request such as this, the `play.html` page is rendered.  
A `POST` request can be made by visiting `play.html`, clicking "Join Network Game", and submitting the room code form.
In this case; the `roomCode` is retrieved from the `POST` data, and a query is made to the `Game` model; looking for any existing games with a matching `roomCode`.
If a game is not found, the `play.html` page is re-rendered with an error message. Other wise, the code checks whether the game is a local or network game by  
comparing `player1` to `player2`. If they're the same, the game is local and the player is redirected to `/play/local?room=*roomCode*`. Otherwise the game is a  
network game and the player is redirected to `/play/network?room=*roomCode*`.


`localGame`
When visiting this page, the `GET` data is first checked for a room code. If there is no room code present; it's assumed the player is attempting to start a new game.  
`generateRoomCode` is called, to create the room code, and a new `Game` record is created and saved to the database. The page is then re-rendered; this time passing in the  
room code as a `GET` request. This step is done to prevent a new game from being created any time the user refreshes the page while playing the game.

If, however, there is a room code present in the `GET` data, then a query is made to the `Game` model to retrieve the specific game that matches the room code.
The `localGame.html` page is then rendered, passing in the games id. The pages JavaScript then takes over and renders the game on the page for the player.


`networkGame` works very similarly to `localGame`.  
If there is no room code present in the `GET` data, a code is generated, and a new `Game` record is created in the database.  
In this case, the user will be recorded as `player1` and redirected to `/play/network?room=*roomCode*`.  

If a room code is present in the `GET` data, then the matching game is pulled from the database.  
If the user is already listed as either `player1` or `player2`, then the `networkGame.html` page is rendered, passing in the game ID and room code  
for the page JavaScript to take over and display the game.  

If, however, the user is not listed as a player, and the games `player2` slot is empty; then the user will be recorded as `player2`, the DB entry  
updated and saved, and the user is redirected to `/play/network?room=*roomCode*` for the game to begin.


`review`
When visiting this page, first a query is made to the `Game` database model; requesting any game where the user is listed as `player1` or `player2`.  
The query is stored in `gameQuery`, and an empty list called `games` is created.
The `gameQuery` is then iterated through in a `for` loop.  
If the game is still active (`isActive=True`), then the record is skipped.
For each query where `isActive=False`, an empty dictionary object called `game` is created. In this loop, some information will be extrapolated from the query objects,  
such as the game type (network or local), the name of the users opponent, the outcome of the game (win, lose, or draw), and the games room code.
This `game` dictionary is then added to the `games` list.  

Finally, `review.html` is rendered, passing in the `games` list; which now contains all of the data that needs to be displayed on the page to the user.
Clicking a link to a game on `review.html` will direct the user to the `reviewGame` route, passing in the room code of the game in a `GET` request.


`reviewGame`
This route simply checks the `GET` data for a room code, queries the `Game` database model for a matching game,  
and renders `reviewGame.html`; passing in the games id, room code, player1, and player2. The pages JavaScript then takes over and renders  
the game for the player to review.


`spectate`
The user can access this route at any time by clicking the **Spectate** link in the navbar. When accessed this way; the `spectate.html` page is rendered,  
which presents a form to the user to enter a room code.  
When this route is accessed by a `POST` request method; via the form on `spectate.html`, then the room code is extracted from the `POST data`,  
and a query is made to the `Game` database model to find a game that matches the room code.  
Finally, the `spectateGame.html` page is rendered, passing in the games ID, where the pages JavaScript will then take over to display the game.


### ChessEngine.py


### JavaScript

