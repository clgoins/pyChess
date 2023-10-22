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


The final 6 routes are API routes that are used for the JavaScript frontend to communicate with the ChessEngine backend.

`getGameState` takes a game ID as a `GET` parameter, and calls `ChessEngine.generateBoardState()`.
The resulting dictionary object is then returned as a JSON object. 


`getMoveList` takes a game ID as a `POST` parameter and makes a query to the `Move` database model. A QuerySet is created containing every `Move` object  
that's associated with the given game ID. Some information is extracted from this QuerySet and returned as a JSON object to the front end.


`checkMoves` takes a `gameState` and a piece ID as a `POST` parameter and calls `ChessEngine.checkPieceMoves()`. The resulting list is then  
returned as a JSON object.


`submitMove` takes a game ID, a piece object, and a desired position as `POST` parameters. These are then passed to `ChessEngine.move()`. If `True` is returned;  
then the move is valid and a new `Move` database entry is created and saved. 


`checkForWinCondition` takes a game ID and a player color, and checks a few different cases to see if an end game condition has been reached.  
First, `ChessEngine.checkForInsufficientMaterial()` is called. This checks if there are too few pieces remaining on the board for a win condition to be reached.  
If the chess engine returns `True`, then the `Game` database entry is updated with `isActive = False`, and this function returns `"message":"draw"` to the front end, resulting in a draw.  
"Insufficient material" is defined by Chess.com as `King vs King`; `King & Bishop vs King`; `King & Knight vs King`; and `King & Bishop vs King & Bishop`, where  
both bishops occupy the same colored square.

If a draw by insufficient material has not occurred, the next step is to count the legal moves available to the current player.  
If this number is 0, the game ends in either a checkmate or a stalemate. A call is made to `ChessEngine.isInCheck()` to determine which.
If this number is -1, it indicates the player has moves remaining, but only the King can move. In this case; the opposing players moves are also counted.  
If the opposing player also returns -1 moves, the game ends in a stalemate. This can happen when there are still Pawns on the board which may be stuck in gridlock.  
In this case, `ChessEngine.checkForInsufficientMaterial()` will return False, even though the game is essentially down to King vs King, which is still defined as a draw.

If these checks all pass, this function returns `"message":"no win"` to the front end, and the game resumes.


`generateRoomCode` is the final function here. This is just a supporting function that creates a new room code when needed.  
A random string of 6 uppercase letters and numbers are created.  
Then a query is made to the `Game` database model. If a game is found with the new room code; then the function loops back and generates a new code.
If no game is found with the newly created code, then the code is considered "good" and will be returned.


### ChessEngine.py

This file contains 12 functions which make up the backend portion of the game itself. 
I'll only provide a brief description of the purpose of each function since the rules to Chess and the game itself are a  
little outside the scope of this projects requirements. I will comment that this ended up being a huge undertaking, and in retrospect I would have chosen a different  
game had I realized how complicated the rules to chess can be.

Before diving into the file function-by-function, I'll lay out the structure of a `boardState`. This is a JSON object that is core to all of the games logic, and used  
to draw the game board at any different point during a game. As such it gets passed between the front and back end often.

A `boardState` looks like this: 

```
"id": 434, 
"roomCode": "8A2XNA", 
"player1": "cg", 
"player2": "chris", 
"turnNumber": 0, 
"pieces": 
    [{"id": 0, 
    "color": "dark", 
    "type": "rook", 
    "rank": 0, 
    "file": 0, 
    "captured": false, 
    "hasMoved": false}, 
    
    {"id": 1, 
    "color": "dark", 
    "type": "knight", 
    "rank": 1, 
    "file": 0, 
    "captured": false, 
    "hasMoved": false}, 
    .  
    .  
    .  
    {"id": 31, 
    "color": "light", 
    "type": "rook", 
    "rank": 7, 
    "file": 7, 
    "captured": false, 
    "hasMoved": false}]
```

It begins with a few details about the game: its ID and room code, the usernames of player1 and player2, the number of turns that have taken place,  
and a large block called "pieces". The "pieces" block is split into 32 sections; one for each piece in the game, and contains a few pieces of identifying  
information: and id number, a color (either 'light' or 'dark'), a type ('pawn', 'rook', 'queen', etc), a rank and file, and two boolean values "captured" and "hasMoved".  
The rank and file store the pieces current position. Rank is the horizontal coordinate, and File is the vertical coordinate. These are integers from 0-7, with (0,0) being  
the top left corner of the board. 

Since writing this code I've discovered much more concise ways to convey this information. There is a standarized system called *FEN Notation* which accomplishes the same purpose in  
one line of text. If I were to write this project again from the ground up, that's the approach I would use. With that being said, I came up with the current system myself without any  
outside help, and switching to FEN Notation would have required significant code rewriting, so I elected to stick with it through the end of the project.


Looking closer at the individual functions that make up my Chess Engine:

`CreateNewBoard` simply takes a `Game` object from the database and generates a new board state as seen above. Each piece has its `captured` and `hasMoved` flags set to False,  
and their positions are set according to Chess rules for starting a new game.


`CheckPieceMoves` is by far the largest function in this file. It takes a `boardState` and a `pieceID`. The purpose of this function is to return a list of every legal move  
that the given piece can make. The function starts by generating a list of occupied spaces on the board to compare any possible move against, called `boardPieces`.  
Then a few blocks contain special cases for Pawns which have unique movement patterns compared to the other pieces. If the given piece in question is a Pawn, the first block  
checks if the Pawn can move diagonally to capture an enemy piece. The second block checks if the Pawn can perform a move known as *En Passant*. These unique moves are further  
complicated by the fact that a player cannot make a move that would place their own King in check. At the end of each block a "virtual game state" is created; which is simply  
a `boardState` that shows what the game would look like on the next turn if the move were allowed to happen. If the players own King is in check in this `virtualGameState`, then  
the move is not legal and is discarded as an option. 

If the given piece is a Rook, then the following block will examine whether a move called *Castling* is allowed. The king is not allowed to move through Check at any point  
during this movement, so several `virtualGameStates` need to be created to examine the outcome at each step of the move before declaring it legal.  

Finally, the last block checks for any standard move the given piece is allowed to make. A call is made to `getMovementPattern()` and `getMovementDistance()` to determine  
which directions and how many spaces a piece is allowed to move. Then each possible move is compared against the `boardPieces` list. A piece may not move into a space occupied  
by a same-colored piece; and it may move into but not *through* a space occupied by an opposite colored piece. A `virtualGameState` is created for the result of each possible move,  
and if the move would put the players own King in check, the move is discarded.

Each time a possible move is checked and declared "legal"; it's coordinateds are added into a list called `validMoves` as a tuple (x,y). Once every possible move has been  
examined for the given piece, `validMoves` is then returned.


`CountValidMoves` makes a call to `checkPieceMoves` for each piece that a given player has remaining on the board. The total number of legal moves for a player is then counted,  
and that count is used to determine if the game has reached a win or draw condition. In the special case that a player has legal moves, but ONLY the King is allowed to move,  
a -1 is returned. This is useful for detecting stalemate conditions where both players can only move their Kings while the other pieces on the board are in some type of gridlock.


`CheckForInsufficientMaterial` looks at the number and types of pieces that both players have remaining on the board. If there is "insufficient material" on the board  
to reach a win condition, the game is declared a draw.


`isInCheck` takes a board state and a player color, and returns True if that player is currently in check, or False if not.
This function starts at the position of the players King, and begins checking one space at a time in a given direction until either the edge of the board or another piece is  
found. If a piece is found, the game checks if that piece is an opponents piece, and if they are able to attack the players King on the next turn. If so, the function returns  
True, otherwise the function returns to the location of the King and begins stepping away again in the next direction. The final block checks 8 specific spaces around the King  
for the presence of an enemy Knight. If all of these tests complete without finding a check, the function returns False.


`move` takes a game ID, piece, and position, and returns True or False if the move is legal. It makes a call to `checkPieceMoves()`, and checks that the provided position  
is contained somewhere in the returned list. If so, the function returns True, and the move is added to the `Move` database.


`GenerateBoardState` is the function responsible for re-creating the state of the board when an in-progress game is resumed.  
It begins by calling `createNewBoard()`, and then makes a call to the `Move` database model to get a list of every move made associated with the game in question.  
Then for each move entry, it will update the board state to reflect the pieces new positions, and return the final `boardState` object.


`SimulateMove` is used by `CheckPieceMoves` for determining whether a move will place a players King in check. It begins by creating a deep copy of the current `boardState` object  
(called `virtualBoardState`) so that data can be manipulated without changing the main game. Then, using similar logic to `GenerateBoardState`, the move that  
needs to be simulated is performed on the `virtualBoardState`. This state is then returned to the calling method where it can be analyzed as needed.


`CoordToRankFile` takes a position tuple (x,y) and converts it to the conventional rank-file system humans are used to reading, where "A1" is the bottom left  
square and "H8" is the top right square.

`RankFileToCoord` does the opposite, where it takes a 2 character string and converts it to an integer tuple in the form (x,y) to make it easier to do math.


`GetMovementPattern` takes a piece object and returns a list of tuples that describe which directions a piece is ordinarily allowed to move, with no respect to the  
distance that the piece can normally move.

`GetMovementDistance` takes a piece object and returns an integer distance that a piece is ordinarily allowed to move, with no respect to the direction that the piece  
can normally move.



### JavaScript

The JavaScript used on the site is split into four main scripts, seen on `localGame.html`, `networkGame.html`, `spectateGame.html`, and `reviewGame.html`.  
For the most part, the scripts are functionally the same with a few small differences depending on the game mode. For the sake of brevity, I'll be detailing  
the network game code, since that's the script that the other 3 are based on, and then I'll spend some time at the end of this section to highlight the main differences  
between the four.

The JavaScript portion of the code makes up the front end portion of the chess engine. This part is responsible for taking user input and drawing the board and pieces on the screen.  
Communication with the backend is done through the use of `fetch` requests made to the API routes detailed in the **Djago** section of this readme.  


The first portion of the code runs as soon as the page is finished loading. 
It starts by adding an event listener for when the user resizes the browser window, calling `setBoardAspectRatio`.  
Handling the board sizing through JS is preferrable because I ended up with some weird artifacts trying to do it through raw CSS.  
Certain cases where the page was right on the edge of switch to the vertical layout would cause the spaces to deform and spread out which was undesirable.

The script then defines an empty dictionary to hold the board state later on, and grabs the game ID, the users username, and the pages CSRF token off the page.  
Three other variables are declared to be used with game logic later on; `checkingMove`, `activePiece`, and `updateTimer`.
The final variable `killClickHandlers` is set up; which is used at the end of the game to deactivate all of the click event handlers on the page to prevent further input.  

`drawBoard()` and `getGameState()` are called and some of the info panels on the board are filled in with the players color and opponent name, etc.

Finally the game checks if a second player has joined, and calls `startGame()` if so. If not, `checkForUpdates()` is called every 15 seconds until a second player is found.  


`checkForUpdates()`
This function is the core of what makes online multiplayer work. The idea is that the frontend has it's own copy of the current game state in memory. A fetch request is  
sent to the `gameState` API route; where the backend will generate a new game state based on the information recorded in the database. If this newly returned game state  
is different from the currently stored game state; it indicates that the opposing player has made their move, and the game can now progress. This function is intended  
to be run via `setInterval()`; so if no change is detected, the function can exit, doing nothing, and will run another check on the next interval.  

The first thing the function checks is the name of player2. If the currently stored state has no name for player2, that indicates the game has just been created.  
If the newly returned state, however, does show a name for player2, than it can be deduced that a second player has just joined the game. The currently stored game state  
will be updated with the newly returned state, and `startGame()` is called, which is the entry point for the games main loop.  

If this function runs, and a name is already saved for player2 in the current game state; this indicates the game is already in progress. In this case, the function  
is instead checking for the opposing player to take their turn, where it can then pass control back to the logged in player. The board and the pieces are drawn to  
the screen, the status message and the move list are updated in the information panel; and `clearInterval()` is called to stop this function from running again until  
another `setInterval()` is invoked at the end of the players turn.  


`startGame()`
This function is the entry point for the games main loop. Once the page is loaded and `checkForUpdates()` determines that a second player is present, this will be the  
first function called. It starts by determining whose turn it is. For simplicity, the player who creates the game is always player1, and always plays as light colored  
pieces. Light pieces always move first, per Chess rules. Therefore, by checking whether the current turn number in the current game state is odd or even, it can  
be determined whose turn it is to move. Player1 will move on even numbered turns, and player2 on odd numbered turns. 

If it is currently the logged in users turn, `clearInterval()` is called, which will ensure the database is not being polled for updates. Otherwise, `setInterval()`  
is called to run `checkForUpdates()` every 15 seconds. The information panel is then updated with the opponents username, the board and pieces are drawn, the status  
and move list panels are populated, and the game checks for a win condition. `checkForWinCondition()` is run once when the game is first loaded, and then again at the end  
of every turn.


`getGameState()` is a simple asynchronous function that makes a fetch request to the `gameState` API route, and returns the newly generated state.  


`updateMoveList()` makes a fetch request to the `moveList` API route. A `<div>` element is made for each item in the returned move list, which contains text details  
about which turn the move took place on, which piece moved, and which space the piece moved to. These `<div>` elements are then added to the on-screen element with the  
id "moveList". This div is the bottom-most panel in the information box (either to the right of or below the chess board, depending on screen orientation). This results in the player seeing a list of every move made  
in the game thus far.


`updateStatus()` is a simple check to see whose turn it is, and then displays that users name in the  
top-most box of the information panel.


`drawBoard()` bears the responsibility of drawing the chess board itself, and attaching click event handlers to each  individual space. The board itself is a `<div>` element with its display set to `grid`. 
A for loop iterates 8 times, creating 8 child divs with the class "boardRow", and a nested for loop iterates 8 more times  
for each row, populating the row with 8 child div elements, with the class name alternating between `lightCell` and  
`darkCell`. This results in the full 8x8 checkerboard pattern on screen.  
Each cell element is given an ID in the format "pX_Y", where X and Y are the cells coordinates, from 0-7. The "p" at the  
start stands for "position" and is only there because HTML apparently does not allow an elements ID to start with a number.  
Finally each cell is given a click event listner which will call `clickCell()` before it is appened to the parent row.  

This function contains two large for loops, each one wrapped in an `if` statement, checking whether the user is playing  
as player1 or player2. This is unique to the Network Game mode, and is intended to draw the board such that the cell IDs  
are labelled in reverse if the player is playing as dark pieces. The point of this is for both players to be able to see  
their own pieces starting at the bottom of the board, which in my opinion feels more natural from a gameplay perspective.  


`drawPieces()` creates an array of Piece objects based on information in the current game state, and then draws each piece  
in the appropriate cell. The cell IDs given to each space in the previous section directly correlate with the `rank` and  
`file` properties of the pieces in the game state. Therefore this is a simple matter of creating an `<img>` tag, and  
loading the correct image based on the pieces `type` and `color` properties, then selecting the cell div with the ID  
`#pX_Y`, where x = `rank` and y = `file`, and appending the `<img>` element as a child. A click event listener is  
also added to each piece, using `clickPiece()` as the callback.

`clickCell()`

`clickPiece()`

`checkMoves()`

`checkWinCondition()`

`endGameAnimation()`

`sleep()`

`setBoardAspectRatio()`
