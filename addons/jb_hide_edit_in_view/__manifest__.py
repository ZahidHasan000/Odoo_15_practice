
{
    "name": "Hide Edit In View by State",
    "summary": "This Module Hide Edit In View By There State",
    "version": "14.0.1.0.1",
    "author": "Joyanto",
    "website": "https://metamorphosis.com.bd",
    "category": "Tools/Tllos",
    "depends": [
        "base",
    ],
    "license": "LGPL-3",
    "data": [
        # 'views/assets.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'jb_hide_edit_in_view/static/src/js/hideedit.js'
        ]
    },
    'sequence': 1,
    "installable": True,
    "auto_install": False,
    "application": True,
}