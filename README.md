# Python Module - Beat Saber Leaderboard Management

## Introduction

It is a Python module to explore, edit and save leaderboards for the Beat Saber, a VR rhythm game where your goal is to slash the beats which perfectly fit into precisely handcrafted music.

This application provides a _Party_ mode, it is a mode to play with friends and family. In contrast with the _Solo_ mode where the scores are uploaded online, the scores of this mode are saved in your VR headset.

On the leaderboard of a song, there are the 10 highest scores. The other scores are removed (or not saved). After some game sessions, the leaderboard of the songs is filled. It becomes difficult to appear on a song leaderboard. When a player tries to fight for the first place, it will pollute the leaderboard with many scores and the scores of other players are removed. When you share your VR headsets with many groups of friends, there are sometimes not enough places in the leaderboard for everybody.

This Python module aims to propose a solution for all the situations described above. Here are some features of the module:

 * Remove some players from the leaderboard. For example, remove all the scores with the label ```No Name```.
 * Rename some players. It is easy to do mistakes when we write the name, now it is possible to correct.
 * Keep only the best scores for each player, to clean the leaderboards.
 * Filter the leaderboard to keep only some scores.
 * Merge multiple leaderboards.
 * Etc...

##  Use Beat Saber Leaderboard

There is below some examples to illustrate the module. To know all the possible features of the module, please see the docstrings of the classes and the methods.

### 1. Get the Leaderboard from the VR Headset

_Remark: this module has been tested only with an Oculus Quest 1. I guess the Beat Saber leaderboard is the same for all types of VR headsets. However, you need to find the procedure to get the Beat Saber leaderboard file yourself._

Oculus Support: https://support.oculus.com/609566816377728/?locale=fr_FR

 * Connect the included USB 2.0 cable to your computer and Oculus Quest headset.
 * Put on your headset and select "Allow" to confirm you want to allow your computer to access files on the headset.
   * On Windows, Oculus Quest will automatically appear as a drive on your computer.
   * On Mac, you'll need to install Android File Transfer to successfully transfer files between your Oculus Quest and computer.
   * On Chromebook/Chrome OS, you'll need to use the Files app to access your Oculus Quest headset.
 * Click and drag files from your Oculus Quest headset on your computer.

The Leaderboard is contained in the file ```LocalLeaderboards.dat``` of the folder ```Android/data/com.beatgames.beatsaber/files```. Copy this file in the folder ```history``` of the project with a name as format ```2021-06-27_LocalLeaderboards.dat```.

The Leaderboard file contains a JSON structure with the following format:

```json
{
    '_leaderboardsData': [
        {'_leaderboardId': '...', '_scores': [...]},
        {'_leaderboardId': '...', '_scores': [...]},
                ...
        {'_leaderboardId': '...', '_scores': [...]},
    ]
}
```

### 2. Clean and Save the Leaderboard

```python
from beatsaber import History
lb = History.get_last_leaderboard()
lb.get_players()
```
```
{
    'bob': 21,
    'loup': 22,
    'alice': 79,
    'alcie': 1,
    'grisgris': 12,
    'blanche': 3,
    'No Name': 1,
    'eve': 2,
    'moutarde': 3,
    'robinson': 2
}
```

#### 2.1. Remove the "No Name"

```python
lb.remove_player("No Name")
lb.get_players()
```
```
{
    'bob': 21,
    'loup': 22,
    'alice': 79,
    'alcie': 1,
    'grisgris': 12,
    'blanche': 3,
    'eve': 2,
    'moutarde': 3,
    'robinson': 2
}
```

#### 2.2. Rename some players

```python
lb.rename_player('alcie', 'alice')
lb.get_players()
```
```
{
    'bob': 21,
    'loup': 22,
    'alice': 80,
    'grisgris': 12,
    'blanche': 3,
    'eve': 2,
    'moutarde': 3,
    'robinson': 2
}
```

#### 2.3. Keep only the best scores for each player

```python
lb.keep_best()
lb.get_players()
```
```
{
    'bob': 15,
    'loup': 10,
    'alice': 29,
    'grisgris': 8,
    'blanche': 3,
    'eve': 2,
    'moutarde': 2,
    'robinson': 2
}
```

#### 2.4. Save the leaderboard

```python
lb.save()
```

### 3. Load a Personalized Leaderboard

```python
from beatsaber import LeaderBoard
lb = LeaderBoard.load()
lb.keep_best()
```

```python
family = ['alice', 'blanche', 'grisgris', 'loup', 'bob']
friends = ['eve', 'moutarde', 'robinson', 'loup']
```

```python
family_lb = lb.filter(family)
family_lb.get_players()
```

```
{'bob': 15, 'loup': 10, 'alice': 29, 'grisgris': 8, 'blanche': 3}
```

```python
friends_lb = lb.filter(friends)
friends_lb.get_players()
```

```
{'loup': 10, 'eve': 2, 'moutarde': 2, 'robinson': 2}
```
```python
family_lb.save('LocalLeaderboards-changed.dat')
```

### 4. Merge the Backup

```python
from beatsaber import LeaderBoard
lb = LeaderBoard.load()
lb.keep_best()
lb.save()
```

Now delete all the files in ```backups``` except the more recent one.

### 5. Explore a Leaderboard

```python
from beatsaber import LeaderBoard
lb = LeaderBoard.load('LocalLeaderboards.dat')
print('Number of songs: %s' % len(lb.get_songs()))
```

```
Number of songs: 39
```

```python
lb.get_players()
```

```
{
    'bob': 21,
    'loup': 22,
    'alice': 79,
    'alcie': 1,
    'grisgris': 12,
    'blanche': 3,
    'No Name': 1,
    'eve': 2,
    'moutarde': 3,
    'robinson': 2
}
```

```python
for i, song in enumerate(lb.get_songs()):
    print('{} - {}'.format(i, song))
```

```
0 - Song "BeatSaber" (Expert)
1 - Song "100Bills" (Expert)
2 - Song "BalearicPumping" (Expert)
3 - Song "BeatSaber" (Normal)
4 - Song "100Bills" (Normal)
5 - Song "BalearicPumping" (Normal)
6 - Song "Breezer" (Normal)
7 - Song "CommercialPumping" (Normal)
8 - Song "CountryRounds" (Normal)
9 - Song "Escape" (Normal)
10 - Song "Legend" (Normal)
11 - Song "LvlInsane" (Normal)
12 - Song "TurnMeOn" (Normal)
13 - Song "BeatSaber" (Easy)
14 - Song "BeatSaber" (Hard)
15 - Song "100Bills" (Hard)
16 - Song "Breezer" (Expert)
17 - Song "CountryRounds" (Expert)
18 - Song "BalearicPumping" (Hard)
19 - Song "FitBeat" (Normal)
20 - Song "FitBeat360Degree" (Normal)
21 - Song "CountryRounds" (Hard)
22 - Song "CommercialPumping" (Expert)
23 - Song "Escape" (Expert)
24 - Song "Legend" (Expert)
25 - Song "LvlInsane" (Expert)
26 - Song "TurnMeOn" (Expert)
27 - Song "TurnMeOn" (Hard)
28 - Song "LvlInsane" (Hard)
29 - Song "Legend" (Hard)
30 - Song "Escape" (Hard)
31 - Song "CommercialPumping" (Hard)
32 - Song "Breezer" (Hard)
33 - Song "100Bills360Degree" (Normal)
34 - Song "CountryRounds" (Easy)
35 - Song "CrabRave" (Normal)
36 - Song "Origins90Degree" (Normal)
37 - Song "Victorious" (Expert)
38 - Song "FitBeat" (Expert)
```

```python
lb['QuestBalearicPumpingHard'].display_scores()
```

```
=== Song "BalearicPumping" (Hard) ===
 - 277088	bob	    FC
 - 271732	loup	
 - 202714	alice	
 - 192157	alice	
 - 171541	alice	
```

## License

MIT License, see ```LICENSE.txt```.