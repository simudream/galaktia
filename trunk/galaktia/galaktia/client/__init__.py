#!/usr/bin/env python
# -*- coding: utf-8 -*-

if __name__ == '__main__':
    import sys
    from galaktia.client.main import main
    reload(sys)
    sys.setdefaultencoding('utf-8')
    main(*sys.argv)

