from functools import cmp_to_key

from sublime import Region
from sublime_plugin import TextCommand


class MoveTextHorizCommand(TextCommand):
    def move_text_horiz(self, edit, direction):
        for region in self.view.sel():
            if region.empty():
                continue

            orig_region = region
            sel_region = Region(region.begin() + direction, region.end() + direction)

            if sel_region.a < 0 or sel_region.b > self.view.size():
                continue

            if direction < 0:
                dest_region = Region(region.begin() + direction, region.end())
                move_text = self.view.substr(region) + self.view.substr(Region(region.begin() + direction, region.begin()))
            else:
                dest_region = Region(region.begin(), region.end() + direction)
                move_text = self.view.substr(Region(region.end(), region.end() + direction)) + self.view.substr(region)

            # Remove selection from RegionSet
            self.view.sel().subtract(orig_region)
            # Replace the selection with transformed text
            self.view.replace(edit, dest_region, move_text)
            # Add the new selection
            self.view.sel().add(sel_region)


class MoveTextLeftCommand(MoveTextHorizCommand):
    def run(self, edit):
        self.move_text_horiz(edit, -1)


class MoveTextLeftTenCommand(MoveTextHorizCommand):
    def run(self, edit):
        self.move_text_horiz(edit, -10)


class MoveTextRightCommand(MoveTextHorizCommand):
    def run(self, edit):
        self.move_text_horiz(edit, 1)


class MoveTextRightTenCommand(MoveTextHorizCommand):
    def run(self, edit):
        self.move_text_horiz(edit, 10)


class MoveTextVertCommand(TextCommand):
    def __init__(self, view):
        super(MoveTextVertCommand, self).__init__(view)
        view.move_text_vert_column = None

    def move_text_vert(self, region, edit, direction):
        if region.empty():
            if direction < 0:
                self.view.run_command('swap_line_up')
            else:
                self.view.run_command('swap_line_down')
            return

        orig_region = region
        move_text = self.view.substr(region)

        # calculate number of characters to the left
        row, col = self.view.rowcol(region.begin())

        # if the last command was a vertical move, use that column
        # the column is stored on the view - each command has its own instance,
        # and we don't want two buffers to modify the same object (e.g. MoveTextVertCommand)
        cmd, _, _ = self.view.command_history(0, True)
        if cmd != 'move_text_up' and cmd != 'move_text_down':
            self.view.move_text_vert_column = col
        elif self.view.move_text_vert_column:
            col = self.view.move_text_vert_column

        dest_row = row + direction

        max_row = self.view.rowcol(self.view.size())[0]
        if dest_row < 0:
            dest_row = 0
        elif dest_row > max_row:
            dest_row = max_row

        self.view.sel().subtract(orig_region)
        self.view.replace(edit, region, '')

        # starting at the destination row at col 0, count off "col" characters
        # it's possible that there aren't enough characters in the destination row,
        # so stop if we end up on the wrong row, or past the buffer
        dest_point = self.view.text_point(dest_row, 0)
        if dest_point is None:
            dest_point = self.view.size()
        else:
            dest_line = self.view.line(dest_point)
            if dest_point + col > dest_line.b:
                dest_point = dest_line.b
            else:
                dest_point = dest_point + col

        insert_region = Region(dest_point, dest_point)
        sel_region = Region(dest_point, dest_point + len(move_text))

        self.view.replace(edit, insert_region, move_text)
        self.view.sel().add(sel_region)
        self.view.show(sel_region)


class MoveTextUpCommand(MoveTextVertCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.move_text_vert(region, edit, -1)


class MoveTextUpTenCommand(MoveTextVertCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.move_text_vert(region, edit, -10)


class MoveTextDownCommand(MoveTextVertCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.move_text_vert(region, edit, 1)


class MoveTextDownTenCommand(MoveTextVertCommand):
    def run(self, edit):
        for region in self.view.sel():
            self.move_text_vert(region, edit, 10)
