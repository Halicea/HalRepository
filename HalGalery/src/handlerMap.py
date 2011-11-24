#{%block imports%}
from Controllers import BaseControllers
from Controllers import ShellControllers
from Controllers import HalWebControllers
from Controllers import HalGalControllers
#{%endblock%}
webapphandlers = [
#{%block ApplicationControllers %}


#{%block BaseControllers %}
('/Login', BaseControllers.LoginController),
('/Login/(.*)', BaseControllers.LoginController),
('/Logout',BaseControllers.LogoutController),
('/AddUser', BaseControllers.AddUserController),
('/WishList', BaseControllers.WishListController),
('/admin/Role', BaseControllers.RoleController),
('/admin/RoleAssociation', BaseControllers.RoleAssociationController),
('/Base/WishList', BaseControllers.WishListController),
('/Base/Invitation', BaseControllers.InvitationController),
#{%endblock%}

#{%block ShellControllers%}
('/admin/Shell', ShellControllers.FrontPageController),
('/admin/stat.do', ShellControllers.StatementController),
#{%endblock%}

#{%block HalWebControllers%}
('/', HalWebControllers.WelcomeController),
#{%endblock%}

#{%block HalGalControllers%}
('/galery/album/(.*)', HalGalControllers.AlbumController(op='view')),
('/galery/album', HalGalControllers.AlbumController),
('/galery/new', HalGalControllers.GaleryController.new_factory(op='new')),
('/galery/edit/(.*)', HalGalControllers.GaleryController.new_factory(op='edit')),
('/galery',HalGalControllers.GaleryController.new_factory(op='index')),

#{%endblock%}
#{%endblock%}
]

