import pickle
import numpy
import re

class Bracket:

    def __init__(self):
        self.num_rounds = 6
        self.round = {}
        self.bracket = {}
        for r in range(self.num_rounds):
            self.round[r] = []  #(64 / 2**r) * [None]
            self.bracket[r] = 2**(self.num_rounds-r) * [None]


    def load_starting_configuration(self, bracket_filename):
        f = open(bracket_filename, 'r') # e.g., '2009_bracket.txt'

        non_white_re = re.compile(r'\w+')

        self.bracket = []
        for line in f:
            line = line.strip()
            m = non_white_re.search(line)
            if m is not None:
                self.bracket.append(line)    


    def opponent_in_round(self, team_id, r):
        """ Find who team <team> played in round <r> """

        for game in self.round[r]:
            date, home_id, away_id, home_score, away_score = game
            if home_id == team_id: return away_id
            elif away_id == team_id: return home_id

        return None


    def make_bracket_structure(self, team_codes=None):
        """ Reorder games within rounds to make bracket structure
        sensible -- that is, the winner of the current round's i^{th} game
        should play in next round's floor(i / 2) game.
        """

        # start at last round and work backwards.  assign previous
        # game of "home" team to the lower game id, and "away" team
        # to the higher game id.
        date, home_id, away_id, home_score, away_score = self.round[5][0]
        winner_id = home_id if home_score > away_score else away_id
        loser_id = away_id if home_score > away_score else home_id
        
        self.bracket[5][0] = winner_id
        self.bracket[5][1] = loser_id

        for r in reversed(range(self.num_rounds)):
            num_games = 2**(self.num_rounds - r)

            if r == 0:  continue

            for i in range(num_games):
                # place winners
                winner_id = self.bracket[r][i]
                self.bracket[r-1][i*2] = winner_id

                loser_id = self.opponent_in_round(winner_id, r-1)
                self.bracket[r-1][i*2+1] = loser_id

        if team_codes is not None:
            # replace ids with team codes
            for r in range(self.num_rounds):
                for i, team_id in enumerate(self.bracket[r]):
                    self.bracket[r][i] = team_codes[team_id]
        

    def print_full(self):
        line_sep = "---"
        blank_sep = "   "
        for i, team_code in enumerate(self.bracket[0]):
            line = ""
            first_blank = True
            for r in range(self.num_rounds):
                if team_code in self.bracket[r]:
                    line += "%s%s" % ("" if r == 0 else line_sep, team_code)
                else:
                    ii = i
                    r1 = r+0
                    r2 = r+1

                    if first_blank:
                        line += "%s" % blank_sep
                        first_blank = False
                        
                    if ii % (2**r2) <= ii % (2**r1): line += "  |%s"  % blank_sep
                    else: line += "   %s" % blank_sep
            print line

            if i == len(self.bracket[0]) - 1:  break
            
            for n in [4, 16]:  # print extra space at these intervals
                if (i+1) % n == 0:
                    alt_line = "   " + line[3:]
                    print alt_line
        print


    def simulate_game(self, team1_code, team2_code):
        team1_id = self.team_code_to_id(team1_code)
        team2_id = self.team_code_to_id(team2_code)

        s_hat1 = numpy.sum(self.offenses[team1_id] * self.defenses[team2_id])
        s_hat2 = numpy.sum(self.offenses[team2_id] * self.defenses[team1_id])

        team1_name = self.team_code_to_name(team1_code)
        team2_name = self.team_code_to_name(team2_code)        

        print "%s %s, %s %s" % (team1_name, s_hat1, team2_name, s_hat2)
        return (s_hat1, s_hat2)


if __name__ == '__main__':
    b = Bracket()

    # If you want to simulate an individual game, you need Yahoo's team code,
    # then just use the simulate_game method.
    #b.simulate_game('mbp', 'aah')
    #b.simulate_game('nav', 'laq')
    #b.simulate_game('nav', 'mbp')
    #b.simulate_game('nav', 'aah')    

    