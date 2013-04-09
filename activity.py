#    This file is part of Cell Management.

#    Cell Management is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Cell Management is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Cell Management.  If not, see <http://www.gnu.org/licenses/>.


import olpcgames
from olpcgames import activity
from gettext import gettext as _

class Activity(activity.PyGameActivity):
    
    game_name = 'cells'
    game_title = _('Cells')
    game_size = None

    
