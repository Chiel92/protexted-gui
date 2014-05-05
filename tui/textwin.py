"Module containing TextWin class."""
import curses
from .win import Win


class TextWin(Win):

    """Window containing the text"""

    def __init__(self, width, height, x, y, session):
        Win.__init__(self, width, height, x, y, session)

    def draw(self):
        """Draw the visible text in the text window."""
        selection = self.session.selection
        text = self.session.text
        labeling = self.session.labeling

        # Find a suitable starting position
        length = len(text)
        position = move_n_wrapped_lines_up(text, self.width,
                                           max(0, selection[0][0]),
                                           int(self.height / 2))

        # Find the places of all empty selected intervals
        empty_intervals = [beg for beg, end in reversed(selection)
                           if end - beg == 0]

        # Draw every character
        while 1:
            try:
                if position >= length and not empty_intervals:
                    self.draw_line('EOF', self.create_attribute(bold=True), silent=False)
                    break

                # Draw possible empty selected interval at position
                if empty_intervals and empty_intervals[0] == position:
                    self.draw_string('ε', self.create_attribute(reverse=True), silent=False)
                    empty_intervals.remove(empty_intervals[0])
                    continue

                reverse = False
                color = 0
                char = text[position]

                # Apply reverse attribute when char is selected
                if selection.contains(position):
                    reverse = True
                    # display newline character explicitly when selected
                    if char == '\n':
                        char = '↵\n'

                # Apply color attribute if char is labeled
                if position in labeling:
                    for i, label in enumerate(['string', 'number', 'keyword', 'comment']):
                        if labeling[position] == label:
                            color = 10 + i

                attribute = self.create_attribute(reverse=reverse, color=color)

                self.draw_string(char, attribute, silent=False)
                position += 1
            except curses.error:
                # End of window reached
                break


def move_n_wrapped_lines_up(text, max_line_width, start, n):
    """Return position that is n lines above start."""
    position = text.rfind('\n', 0, start)
    if position <= 0:
        return 0
    while 1:
        previousline = text.rfind('\n', 0, position - 1)
        if previousline <= 0:
            return 0
        n -= int((position - previousline) / max_line_width) + 1
        if n <= 0:
            return position + 1
        position = previousline
