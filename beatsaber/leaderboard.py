import json
import os
import datetime

from .song import Song
from .score import Score

class History:
    DEFAULT_FOLDER = 'history'

    @classmethod
    def get_last_leaderboard(cl, folder=DEFAULT_FOLDER):
        """ Return the LeaderBoard contained in the last file of the given folder.
        The file order is the lexicographic order.

        :param folder: the folder name
        :type folder: string
        :rtype: a LeaderBoard instance
        """
        filenames = []
        for filename in sorted(os.listdir(folder)):
            filename = os.path.join(folder, filename)
            if os.path.isfile(filename) and os.path.splitext(filename)[1] == '.dat':
                filenames.append(filename)
        return LeaderBoard.load(filenames[-1])

class Backup:
    DEFAULT_FOLDER = 'backups'
    
class LeaderBoard:
    """ A BeatSaber LeaderBoard with songs and all the corresponding scores.

    :param songs: list of the songs of the LeaderBoard
    :type songs: list of Song instances
    """
    def __init__(self, songs):
        self._leaderboardsData = songs
        
        # Cache
        self.__song_pos = {song.get_leaderboardId(): i for i, song in enumerate(songs)}

    @classmethod
    def pull(cl):
        """ Recuperate the current BeatSaber LeaderBoard of the connected VR headset.

        :rtype: a LeaderBoard instance
        """
        raise NotImplementedError()

    def push(self):
        """ Set the BeatSaber LeaderBoard of the connected VR headset with the current LeaderBoard.
        """
        raise NotImplementedError()

    @classmethod
    def load(cl, path=None):
        """ Return the BeatSaber LeaderBoard encoded in the given file or directory.
        See ``load_file`` and ``load_dir`` for more details. If ``path`` is None, it will
        load the LeaderBoard of the backup. See ``load_from_backup`` for more details.

        :param path: the path of the file (or directory) which contains the LeaderBoard
        :type path: string
        :rtype: a LeaderBoard instance
        """
        if path is None:
            return cl.load_from_backup()
        elif os.path.isdir(path):
            return cl.load_dir(path)
        else:
            return cl.load_file(path)

    @classmethod
    def load_file(cl, filename):
        """ Return the BeatSaber LeaderBoard encoded in the given file.

        :param filename: the file name of the LeaderBoard
        :type filename: string
        :rtype: a LeaderBoard instance
        """
        with open(filename, 'r') as _file:
            obj = json.loads(_file.read())
            return cl.from_json(obj)
    
    @classmethod
    def load_dir(cl, dirname, correct_extensions=['.dat']):
        """ Return the BeatSaber LeaderBoard represented by all the files of a directory

        :param dirname: the directory name
        :type dirname: string
        :param correct_extensions: the file extensions of the LeaderBoard
        :type correct_extensions: list of strings
        :rtype: a LeaderBoard instance
        """
        global_leaderboard = cl([])
        for filename in os.listdir(dirname):
            filename = os.path.join(dirname, filename)
            if os.path.isfile(filename):
                _, extension = os.path.splitext(filename)
                if extension in correct_extensions:
                    global_leaderboard += cl.load_file(filename)
        return global_leaderboard

    @classmethod
    def load_from_backup(cl):
        """ Return the BeatSaber LeaderBoard represented by all the files of the backup directory.
        The backup directory is given by ``Backup.DEFAULT_FOLDER``.

        :rtype: a LeaderBoard instance
        """
        return cl.load_dir(Backup.DEFAULT_FOLDER)

    def save(self, filename=None, must_be_valid=True):
        """ Save the LeaderBoard in a file. If no filename is given, it will save the
        LeaderBoard in the backup. See ``save_in_backup`` for more details.

        :param filename: the filename where the LeaderBoard will be saved
        :type filename: string
        :param must_be_valid: if True and if a filename is given, the saving is performed only if the LeaderBoard is valid (cf ``is_valid``)
        :type must_be_valid: boolean
        """
        if filename is None:
            self.save_in_backup()
        else:
            assert not must_be_valid or self.is_valid()
            #assert not os.path.exists(filename), 'Already exists!'
            
            with open(filename, 'w') as _file:
                _file.write(json.dumps(self.to_json()))
    
    def save_in_backup(self):
        """ Save the LeaderBoard in the backup. It will create a new file in the backup directory,
        with the name "%Y-%m-%d_%H-%M-%S_LocalLeaderboards.dat".
        """
        now = datetime.datetime.now()
        filename = now.strftime('%Y-%m-%d_%H-%M-%S_LocalLeaderboards.dat')
        if not os.path.exists(Backup.DEFAULT_FOLDER):
            os.mkdir(Backup.DEFAULT_FOLDER)
        self.save(os.path.join(Backup.DEFAULT_FOLDER, filename), must_be_valid=False)
        
    ### Getters
    def get_songs(self):
        """ Return the list of songs of the LeaderBoard (with all the scores)

        :rtype: a list of Song instances
        """
        return self._leaderboardsData
    
    def __getitem__(self, index):
        """ Return the song selected by the index. If ``index`` is a string,
        return the song with ``index`` as ID. If ``index`` is an integer,
        return the song with ``index`` as position in the list returned by ``get_songs``.
        
        :rtype: a Song instance
        """
        if type(index) is str:
            # "index" is a song ID
            pos = self.__song_pos[index]
            return self._leaderboardsData[pos]
        else:
            # "index" is the position of the song
            return self._leaderboardsData[index]
        
    def get_players(self):
        """ Return the dictionary which associates the (user)name of each player with
        each number of occurencies in the LeaderBoard. For example,

        .. code-block:: python

            {
                'Blanche': 42,
                'Fleur': 2,
                'Loup': 23,
                'Logan': 35,
            }  

        means that Blanche appears 42 times in the LeaderBoard, that Fleur appears 2 times...

        :rtype: dict{string => integer}
        """
        players = {}
        for song in self._leaderboardsData:
            song_players = song.get_players()
            for name, number in song_players.items():
                try:
                    players[name] += number
                except KeyError:
                    players[name] = number
        return players
    
    ### Setters
    def rename_player(self, old, new):
        """ Rename a player in all the songs of the LeaderBoard.
        This operation modifies the current object.

        :param old: the player name which will be renamed
        :type old: string
        :param new: the new player name
        :type new: string
        """
        for song in self.get_songs():
            song.rename_player(old, new)

    def remove_player(self, name='No Name'):
        """ Remove a player from all the songs of the LeaderBoard
        This operation modifies the current object.

        :param name: the player name which will be removed
        """
        for song in self.get_songs():
            song.remove_player(name)
            
    def keep_best(self, keep_FC=True, name=None):
        """ Clean the LeaderBoard by keeping the best score for
        each player in each song. If ``keep_FC`` is true, keep also
        the best score with "Full Combo" for all players. If a name is given,
        only the scores of this player will be cleaned.
        This operation modifies the current object.

        :param keep_FC: if True, keep also the best score with "Full Combo" for all players.
        :type keep_FC: boolean
        :param name: name of the player for which the scores are cleaned, optional
        :type name: string
        """
        for song in self.get_songs():
            song.keep_best(keep_FC, name)
            
    def truncate(self, limit=10):
        """ Truncate the leaderboards for all songs. Only the best scores
        are kept. Return the removed scores.

        :param limit: maximal number of scores for each song after truncated
        :type limit: integer
        :rtype: list of list of Score instances
        """
        too_much = []
        for song in self.get_songs():
            too_much.append(
                song.truncate(limit)    
            )
        return too_much
            
    def is_valid(self):
        """ Indicate if the LeaderBoard is ready/valid to be used in production.
        It is the case if each song has at most 10 scores.

        :rtype: boolean
        """
        for song in self.get_songs():
            if not song.is_valid():
                return False
        return True
        
    def filter(self, names):
        """ Return a new LeaderBoard with only the scores of the given players.

        :param names: the list of player names for which the scores are kept
        :type names: list of string
        :rtype: a LeaderBoard instance
        """
        return type(self)(
            [song.filter(names) for song in self.get_songs()]
        )

    def add_songs(self, songs, *args):
        """ Add songs in the LeaderBoard. If a song was already in the LeaderBoard,
        then its scores will be added in the existing song.
        This operation modifies the current object.

        :param songs: the list of the added songs
        :type songs: list of Song instances
        """
        # Get the list of scores
        try:
            _ = (e for e in songs)
            assert len(args) == 0, 'If the first argument is iterable, it must be the only argument.'
        except TypeError:
            songs = [songs] + list(args)
        # Checking
        for song in songs:
            assert isinstance(song, Song)
        # Adding
        for song in songs:
            id = song.get_leaderboardId()
            try:
                pos = self.__song_pos[id]
                csong = self._leaderboardsData[pos]
                self._leaderboardsData[pos] = csong + song
            except KeyError:
                self._leaderboardsData.append(song)
                self.__song_pos[id] = len(self._leaderboardsData)-1        
    
    def add_song(self, song):
        """ Add a Song instance in the LeaderBoard.
        See ``add_songs`` for more details.
        This operation modifies the current object.

        :param song: the added song
        :type song: a Song instance
        """
        self.add_songs([song])
    
    def __add__(self, other):
        """ Add the scores of two LeaderBoards. It will create a new LeaderBoard instance.
        See ``add_songs`` for more details about the merging.

        :rtype: a LeaderBoard instance
        """
        lb = LeaderBoard(self.get_songs())
        lb.add_songs(other.get_songs())
        return lb

    ### Misc
    @classmethod
    def from_json(cl, obj):
        """ Return the BeatSaber LeaderBoard represented by the given JSON structure.
        The JSON structure must be the same than the used one in Beat Saber application.

        :param obj: the JSON structure
        :param obj: dict
        :rtype: a LeaderBoard instance
        """
        return cl(list(map(Song.from_json, obj['_leaderboardsData'])))
        
    def to_json(self):
        """ Convert the BeatSaber LeaderBoard into a JSON structure.
        The used JSON structure is the same than the used one by the Beat Saber application.
        
        :rtype: dict
        """
        return {
            '_leaderboardsData': [song.to_json() for song in self._leaderboardsData],
        }
    