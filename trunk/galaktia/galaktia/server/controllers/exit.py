#!/usr/bin/python
# -*- coding: utf-8 -*-


from galaktia.protocol.controller import MessageController
from galaktia.protocol.operations.exit import *


class LogoutRequestController(MessageController):

    def __init__(self, session_dao, dao_resolver):
        MessageController.__init__(self, session_dao, dao_resolver)
        self.char_dao = dao_resolver.char
        self.user_dao = dao_resolver.user

    def _process(self, session):
        if session is not None:
            character = self.char_dao.get_by(id=session.character_id)
            user = self.user_dao.get_by(id=character.user_id)
            username = user.name
            yield LogoutResponse(session=session)
            self.char_dao.dismiss(character)
            for aSession in self.session_dao.get_logged():
                yield UserExited(session_id=session.id,
                                 session=aSession,
                                 username=username)
            self.session_dao.delete(session)
