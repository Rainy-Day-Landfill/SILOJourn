#!/usr/bin/python3

import argparse
import os, sys
import configparser
from dialog import Dialog
from datetime import datetime
import subprocess
import re

solution_description="Journaling system for daily needs."
epilog="Designed and written by Chris Punches.\n SILO GROUP LLC, 2019.  ALL RIGHTS RESERVED."


class Config():
    def get_conf_location(self):
        home=os.getenv("HOME")
        return "{}/.silojourn.ini".format( home )

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read( self.get_conf_location() )
        self.journal_path = self.config['filesystem']['journal']
        self.editor = self.config['tools']['editor']

    def get_journal_path(self):
        return self.journal_path

    def get_editor(self):
        return self.editor


class Journaler():
    def __init__(self, config):
        self.config = config
        self.d = Dialog( dialog="dialog", autowidgetsize=True)


    # generate the filepath for a specific entry
    def _get_entry_filename(self, topic, date):
        # TODO add sanity checks
         return "{0}/{1}_{2}".format( self.config.get_journal_path(), date, topic )


    # open a specific entry for a supplied topic and date
    def _open_entry(self, topic, date):
        subprocess.run( [ self.config.get_editor(), self._get_entry_filename( topic, date ) ] )


    # gemerate the current date in a standard format
    def _get_current_date(self):
        return datetime.today().strftime('%Y-%m-%d')

    # load all entry metadata
    def _get_all_entries(self):
        entry_list = os.listdir( self.config.get_journal_path() )
        return entry_list


    # get all topics for all dates
    def _get_all_topics(self):
        topics = list()
        for item in self._get_all_entries():
            try:
                found = re.search("[0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]_(.+?)$", item ).group(1)
                topics.append( found )
            except AttributeError:
                pass
        return sorted( list( dict.fromkeys( topics ) ) )


    # get all topics for all dates
    def _get_all_dates(self):
        dates = list()
        for item in self._get_all_entries():
            try:
                found = re.search( "([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])_.+?$", item ).group(1)
                dates.append( found )
            except AttributeError:
                pass
        return sorted( list( dict.fromkeys( dates ) ) )


    # get all topics associated with a date
    def _get_topics(self, date):
        topics = list()

        for item in self._get_all_entries():
            try:
                found = re.search("{0}_(.+?)$".format(date), item).group(1)
                topics.append(found)
            except AttributeError:
                pass
        return sorted( list( dict.fromkeys( topics ) ) )


    # get all dates associated with a topic
    def _get_dates(self, topic):
        dates = list()

        for item in self._get_all_entries():
            try:
                found = re.search("([0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9])_{0}".format( topic ), item ).group(1)
                dates.append(found)
            except AttributeError:
                pass
        return sorted( list( dict.fromkeys( dates ) ) )


    # browse topics for a specific date
    def do_topic_browse_by_date(self, date):
        print( "topic browse by date: {}".format( date ) )
        topics = self._get_topics( date )

        menu_choices = list()
        for i in range(len(topics)):
            menu_choices.append(
                ( topics[i], "[{}] total entries.".format( len( self._get_dates( topics[i] ) ) ) )
        )

        code, topic = self.d.menu(
            "Select a topic for date: {0}".format(date),
            choices=menu_choices,
            width=self.d.maxsize()[1],
            extra_button=True,
            extra_label="New...",
            ok_label="Select"
        )

        if code == self.d.OK:
            self._open_entry(topic, date)
            self.do_topic_browse_by_date(date)
        elif code == self.d.EXTRA:
            input_code, input_topic = self.d.inputbox( "Creating a new topic for today: {}".format( date ), width=self.d.maxsize()[1] )
            if input_code == self.d.OK:
                self.do_new_topic( input_topic )
            else:
                self.do_topic_browse_by_date( date )
        else:
            self.do_browse_topics()


    # browse dates for a specific topic
    def do_date_browse_by_topic(self, topic):
        dates = self._get_dates(topic)

        menu_choices = list()
        for i in range(len(dates)):
            menu_choices.append( ( dates[i], "{} total topics.".format(
                len(
                    self._get_topics( dates[i] )
                )
            ) ) )

        code, date = self.d.menu(
            "Select a date for topic: {0}".format( topic ),
            choices=menu_choices,
            width=self.d.maxsize()[1],
            cancel_label="Back",
            ok_label="Select"
        )

        if code == self.d.OK:
            self._open_entry(topic, date)
            self.do_topic_browse_by_date(date)

        else:
            self.do_browse_topics()


    def do_browse_todo_entries(self):
        print( "not yet implemented" )


    # browse topics for all dates
    def do_browse_topics(self):
        topics = self._get_all_topics()

        menu_choices = list()
        for i in range(len(topics)):
            menu_choices.append( ( topics[i], "{} total entries.".format( len( self._get_dates( topics[i] ) ) ) ) )


        code, topic = self.d.menu(
            "Select a topic whose dated entries you want to browse:",
            choices=menu_choices,
            width=self.d.maxsize()[1],
            cancel_label="Back",
            ok_label="Select",
            extra_button=True,
            extra_label="New topic for today..."
        )

        if code == self.d.OK:
            self.do_date_browse_by_topic(topic)
        elif code == self.d.EXTRA:
            input_code, input_topic = self.d.inputbox( "Creating a new topic for today: {}".format( self._get_current_date() ), width=self.d.maxsize()[1] )
            if input_code == self.d.OK:
                self.do_new_topic( input_topic )
                self.do_browse_topics()
            else:
                self.do_browse_topics()


    # browse dates for all topics
    def do_list_dates(self):
        dates = sorted( self._get_all_dates() )

        menu_choices = list()
        for i in range( len( dates ) ):
            menu_choices.append( ( dates[i], "{} total topics.".format( len( self._get_topics( dates[i] ) ) ) ) )

        code, date = self.d.menu(
            "Select a date to browse topics for that date...",
            choices=menu_choices,
            width=self.d.maxsize()[1]
        )

        if code == self.d.OK:
            self.do_topic_browse_by_date( date )


    def do_new_topic(self, topic):
        self._open_entry( topic, self._get_current_date() )


def main():
    parser = argparse.ArgumentParser( description=solution_description, prog="silojourn", epilog=epilog )

    # want these options to be mutually exclusive to cut down on cli complexity

    # should pull up a curses menu list that shows a list of topics for a certain date
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument( "-D", "--date", help="Browse topics by date." )

    # should pull up a curses menu list that shows a list of dates for a certain topic
    topic_group = parser.add_mutually_exclusive_group()
    topic_group.add_argument( "-T", "--topic", help="Browse dates by topic." )

    # should pull up a curses menu that lists all "TO DO" lines in all journal entries in the base.
    # this menu should be able to mark an item as completed in that journal entry with a TUI checkbox
    todo_group = parser.add_mutually_exclusive_group()
    todo_group.add_argument( "-d", "--todo", help="Manage pending tasks.", action="store_true" )

    # should pull up a curses menu to select from all topics for all dates.  selecting a topic pulls up a list
    # of all dates for that topic.
    list_topic_group = parser.add_mutually_exclusive_group()
    list_topic_group.add_argument( "-L", "--list-topics", help="Browse topics for all dates.", action="store_true" )

    # should pull up a curses menu list of all dates.  selecting a date should list topics for that date.
    list_dates_group = parser.add_mutually_exclusive_group()
    list_dates_group.add_argument( "-l", "--list-dates", help="Browse dates for all topics.", action="store_true" )

    # opens a new topic with today's date using the selected editor specified in the config file
    new_entry_group = parser.add_mutually_exclusive_group()
    new_entry_group.add_argument( "-o", "--new-topic")

    args = parser.parse_args()

    config = Config()
    silojourn = Journaler( config )

    if len(sys.argv) > 3:
        parser.print_help()

    elif args.date:
        silojourn.do_topic_browse_by_date( args.date )

    elif args.topic:
            silojourn.do_date_browse_by_topic( args.topic )

    elif args.todo:
            silojourn.do_browse_todo_entries()

    elif args.list_topics:
            silojourn.do_browse_topics()

    elif args.list_dates:
            silojourn.do_list_dates()

    elif args.new_topic:
            silojourn.do_new_topic( args.new_topic )

    else:
        parser.print_help()


if __name__=='__main__':
    main()