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

import re
import gobject

from translate.search import match

from virtaal.models import BaseModel


class TMModel(BaseModel):
    """Translation memory model that matches against translated strings from current file"""

    __gtype_name__ = 'CurrentFileTMModel'
    __gsignals__ = {
        'match-found': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_PYOBJECT,))
    }

    # INITIALIZERS #
    def __init__(self, controller):
        super(TMModel, self).__init__()

        self.controller = controller

        #TODO: tm server connection settings should come from configs
        self.matcher = None
        self.cache = {}

        self.controller.connect('start-query', self.query)
        self.controller.main_controller.store_controller.connect('store-loaded', self.recreate_matcher)


    # METHODS #
    def recreate_matcher(self, storecontroller):
        store = storecontroller.get_store()._trans_store
        self.matcher = match.matcher(store)
        
        
    def query(self, tmcontroller, query_str):
        if self.cache.has_key(query_str):
            self.emit('match-found', query_str, self.cache[query_str])
        else:
            self.cache[query_str] = [_unit2dict(candidate) for candidate in self.matcher.matches(unicode(query_str, "utf-8"))]
            self.emit('match-found', query_str, self.cache[query_str])


def _unit2dict(unit):
    """converts a pounit to a simple dict structure for use over the web"""
    return {"source": unit.source, "target": unit.target, 
            "quality": _parse_quality(unit.othercomments), "context": unit.getcontext()}

def _parse_quality(comments):
    """extracts match quality from po comments"""
    for comment in comments:
        quality = re.search('([0-9]+)%', comment)
        if quality:
            return quality.group(1)