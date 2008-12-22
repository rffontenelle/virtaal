#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2008 Zuza Software Foundation
#
# This file is part of Virtaal.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

from translate.services import tmclient

from virtaal.plugins.tm.basetmmodel import BaseTMModel

class TMModel(BaseTMModel):
    """This is the translation memory model."""

    __gtype_name__ = 'RemoteTMModel'

    default_config = {
        "host" : "localhost",
        "port" : "8080",
        }

    # INITIALIZERS #
    def __init__(self, controller):
        self.load_config()
        url = "http://%s:%s/tmserver" % (self.config["host"], self.config["port"])

        self.tmclient = tmclient.TMClient(url)
        super(TMModel, self).__init__(controller)

    # METHODS #
    def query(self, tmcontroller, query_str):
        if self.cache.has_key(query_str):
            self.emit('match-found', query_str, self.cache[query_str])
        else:
            self.tmclient.translate_unit(query_str, self._handle_matches)

    def _handle_matches(self, widget, query_str, matches):
        """Handle the matches when returned from self.tmclient."""
        self.cache[query_str] = matches
        self.emit('match-found', query_str, matches)