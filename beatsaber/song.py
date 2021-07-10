from .score import Score


class Level:
    EASY = 'Easy'
    NORMAL = 'Normal'
    HARD = 'Hard'
    EXPERT = 'Expert'
    EXPERT_PLUS = 'Expert+'
    
    @classmethod
    def get_all(cl):
        return [Level.EASY, Level.NORMAL, Level.HARD, Level.EXPERT, Level.EXPERT_PLUS]


class Song:
    """ A BeatSaber Song with all the scores.

    :param leaderboardId: the song ID
    :type leaderboardId: string
    :param scores: the list of scores for the song (sorted)
    :type scores: list of Score instances
    """
    def __init__(self, leaderboardId, scores):
        self._leaderboardId = leaderboardId
        self._scores = scores
        # To avoid to clean often the list of scores,
        #   this boolean enables us to track if the current
        #   list of scores has some redundencies.
        self._has_redundencies = False
        
        # Cache
        is_of_level = lambda lvl: (self._leaderboardId[-len(lvl):] == lvl)
        self.__level = list(filter(is_of_level, Level.get_all()))[0]
        self.__title = self._leaderboardId[len('Quest'):-len(self.__level)]
    
    ### Getters
    def get_leaderboardId(self):
        """ Return the song ID.

        :rtype: string
        """
        return self._leaderboardId
    
    def get_level(self):
        """ Return the song level.

        :rtype: string
        """
        return self.__level
        
    def get_title(self):
        """ Return the song title.

        :rtype: string
        """
        return self.__title
        
    def get_scores(self):
        """ Return the list of scores of the song.
        It is sorted to have the highest score is the beginning of the returned list.

        :rtype: list of Score instances
        """
        self._clean_scores()
        return self._scores
        
    def __getitem__(self, num):
        """ Return the score at position "num".

        :param num: the position of the asked score
        :type num: integer
        :rtype: a Score instance
        """
        self._clean_scores()
        return self._scores[num]

    def get_players(self):
        """ Return the dictionary which associates the (user)name of each player with
        each number of occurencies in the song LeaderBoard. For example,

        .. code-block:: python

            {
                'Blanche': 42,
                'Fleur': 2,
                'Loup': 23,
                'Logan': 35,
            }  

        means that Blanche appears 42 times in the song LeaderBoard, that Fleur appears 2 times...

        :rtype: dict{string => integer}
        """
        players = {}
        for score in self.get_scores():
            name = score.get_player()
            try:
                players[name] += 1
            except KeyError:
                players[name] = 1
        return players
    
    ### Setters
    def add_scores(self, scores, *args):
        """ Add scores in the song LeaderBoard.
        To avoid to often clean redundancies and sort the scores, this
        operation is delayed as long as possible.

        :param scores: the list of the added scores
        :type scores: list of Score instances
        """
        # Get the list of scores
        try:
            _ = (e for e in scores)
            assert len(args) == 0, 'If the first argument is iterable, it must be the only argument.'
        except TypeError:
            scores = [scores] + list(args)
        # Checking
        for score in scores:
            assert isinstance(score, Score)
        # Adding
        for score in scores:
            self._scores.append(score)
        self._has_redundencies = True
        
    def add_score(self, score):
        """ Add a Score instance in the song LeaderBoard.
        See ``add_scores`` for more details.

        :param score: the added score
        :type score: a Score instance
        """
        self.add_scores([score])
        
    def __add__(self, other):
        """ Add the scores of two LeaderBoards of the same song.
        It will create a new Song instance.
        See ``add_scores`` for more details about the merging.

        :rtype: a Song instance
        """
        leadboardId = self.get_leaderboardId()
        assert leadboardId == other.get_leaderboardId()
        
        song = Song(leadboardId, [])
        song.add_scores(self._scores + other._scores)
        return song
   
    ### Utility
    def _clean_scores(self):
        """ Sort the scores and remove the redundancies.
        """
        if self._has_redundencies:
            self._scores.sort()

            scores = []
            for score in self._scores:
                if (not scores) or (score != scores[-1]):
                    scores.append(score)

            self._scores = scores
            self._has_redundencies = False

    ### Display functions
    def display_scores(self):
        """ Display the song leaderboard in the standard output.
        """
        print('=== {} ==='.format(str(self)))
        for score in self._scores:
            print(' - {}'.format(score))
                    
    def __str__(self):
        return 'Song "{}" ({})'.format(
            self.get_title(),
            self.get_level(),
        )
    
    def __repr__(self):
        return '<{}>'.format(
            self.__str__(),
        )
        
    def rename_player(self, old, new):
        """ Rename a player in the song LeaderBoard.
        This operation modifies the current object.

        :param old: the player name which will be renamed
        :type old: string
        :param new: the new player name
        :type new: string
        """
        for i, score in enumerate(self._scores):
            if score.get_player() == old:
                score.rename_player(new)

    def remove_player(self, name='No Name'):
        """ Remove a player from the song LeaderBoard
        This operation modifies the current object.

        :param name: the player name which will be removed
        """
        for i, score in reversed(list(enumerate(self._scores))):
            if score.get_player() == name:
                self._scores.pop(i)
            
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
        self._clean_scores()

        rmv_idxs = []
        already = {}
        for i, score in enumerate(self._scores):
            cname = score.get_player()
            fullcombo = score.is_fullCombo()
            if (name is not None) and (cname!=name):
                continue
            
            if cname not in already:
                already[cname] = fullcombo
            elif (keep_FC and not already[cname] and fullcombo):
                already[cname] = True
            else:
                rmv_idxs.append(i)
        rmv_idxs.reverse()
        for i in rmv_idxs:
            self._scores.pop(i)
            
    def truncate(self, limit=10):
        """ Truncate the song leaderboard. Only the best scores
        are kept. Return the removed scores.

        :param limit: maximal number of scores after truncated
        :type limit: integer
        :rtype: list of Score instances
        """
        scores = self.get_scores()
        too_much = scores[limit:]
        self._scores = scores[:limit]
        return too_much
        
    def is_valid(self):
        """ Indicate if the song LeaderBoard is ready/valid to be used in production.
        It is the case if the song has at most 10 scores.

        :rtype: boolean
        """
        return len(self.get_scores()) <= 10
        
    def filter(self, names):
        """ Return a new Song with only the scores of the given players.

        :param names: the list of player names for which the scores are kept
        :type names: list of string
        :rtype: a Song instance
        """
        criteria = lambda score: (score.get_player() in names)
        return Song(
            self._leaderboardId,
            list(filter(criteria, self._scores))
        )

    ### Misc
    @classmethod
    def from_json(cl, obj):
        """ Return the Song represented by the given JSON structure.
        The JSON structure must be the same than the used one in Beat Saber application.

        :param obj: the JSON structure
        :param obj: dict
        :rtype: a Song instance
        """
        return cl(
            leaderboardId=obj['_leaderboardId'],
            scores=list(map(Score.from_json, obj['_scores'])),
        )
        
    def to_json(self):
        """ Convert the Song into a JSON structure.
        The used JSON structure is the same than the used one by the Beat Saber application.
        
        :rtype: dict
        """
        return {
            '_leaderboardId': self._leaderboardId,
            '_scores': [score.to_json() for score in self.get_scores()],
        }
