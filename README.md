# Hacks Bot

This is a discord bot for Foothill College's CS Club's Summer 2020 Hackathon 💬. It supports tracking projects, which are called "hacks".



## Commands

The following are the commands that all users can use:

### hacks list

List all the hacks.

### hacks add "a short title" @user1 [@user2]

Ex. `hacks add "A very cool project" @cooldude`

Add a hack! Make sure to specify a description (quote with " if more than one word) and at least one user with an `@mention`.


### hacks update X "description" [@user1]

Ex. `hacks update 4 "A very cool project"`

Ex. `hacks update 12 "Not sure what this is.." @dude @coder`

Update a hack. A new description is required, and an updated list of members is optional.


### hacks remove X

Ex. `hacks remove 6`

Remove a hack. Tip: use `hacks list` to list all the hacks with their index.


### hacks link X URL

Ex. `hacks link 6 https://github.com/FoothillCSClub/hackbot`

Add a project link to a hack. A URL is required.


### hacks unlink X

Ex. `hacks unlink 6`

Remove a project link from a hack.



## Admin

### hacks send #channel

Ex. `hacks send #announcements`

Send the hackathon info message and the list of hacks into the specified channel. The last sent messages by this command are tracked and are automatically updated when someone modifies the list of hacks.


### hacks delete #channel

Ex. `hacks delete #announcements`

Delete the last tracked info messages from a channel (sent by `hacks send`), if they exist.



## License

[MIT License](LICENSE)
