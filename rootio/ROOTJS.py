
from IPython.display import display
import logging
import json

class ROOTJS(object) :

    LOAD_MIMETYPE   = "application/vnd.rootjs_load.v0+json"
    EXEC_MIMETYPE   = "application/vnd.rootjs_exec.v0+json"
    JS_MIMETYPE     = "application/javascript"
    HTML_MIMETYPE   = "text/html"
    canvas_index    = 0
    active_div_id   = ""

    # def __init__( self ) :
        # self.logger = logging.getLogger( "rootio.ROOTJS" )
    
    @staticmethod
    def load( ) :
        _jsCode = """
            requirejs.config({
                paths: {
                'JSRootCore' : 'https://root.cern.ch/js/notebook//scripts/JSRootCore',
                }
            });
            """
        obj = { 
                ROOTJS.LOAD_MIMETYPE : _jsCode,
                ROOTJS.JS_MIMETYPE : _jsCode
            }
        display( obj, raw=True )
    @staticmethod
    def canvas( **kwargs ) :
        jsDivId = "root_pad_" + str( ROOTJS.canvas_index ) 
        ROOTJS.canvas_index = ROOTJS.canvas_index+1
        # if they passed in a div id then use that instead
        ROOTJS.active_div_id = kwargs.get( 'div', jsDivId )

        obj = { 
                ROOTJS.EXEC_MIMETYPE : kwargs.get('data', None), 
                ROOTJS.JS_MIMETYPE : "",
                ROOTJS.HTML_MIMETYPE : ""
            }
        metadata = {
            ROOTJS.EXEC_MIMETYPE : { 
                    "id" : ROOTJS.active_div_id, 
                    "width" : kwargs.get( 'width', kwargs.get( 'w', 500 ) ),
                    "height" : kwargs.get( 'height', kwargs.get( 'h', 500 ) )
                }
        }

        display( obj, metadata=metadata, raw=True )

    @staticmethod
    def draw( **kwargs ) :
        # create a default canvas if needed
        if "" == ROOTJS.active_div_id and None == kwargs.get( 'div', None ):
            ROOTJS.canvas()

        jsDivId = ROOTJS.active_div_id 
        # if they passed in a div id then use that instead
        div_id = kwargs.get( 'div', jsDivId )

        jsonContent = kwargs.get( 'data', None )
        if isinstance( jsonContent, dict ) :
            jsonContent = json.dumps( jsonContent )
        jsDrawOptions = kwargs.get( 'opts', "" )
        _jsCode =f"""
            require(['JSRootCore'],
                function(Core) {{
                var obj = Core.JSONR_unref({jsonContent});
                Core.draw("{div_id}", obj, "{jsDrawOptions}");
                }}
            );
        """

        obj = { 
                ROOTJS.EXEC_MIMETYPE : kwargs.get('data', None), 
                ROOTJS.JS_MIMETYPE : _jsCode
            }
        metadata = {
            ROOTJS.EXEC_MIMETYPE : { 
                    "id" : div_id, 
                    "width" : kwargs.get( 'width', 500 ),
                    "height" : kwargs.get( 'height', 500 )
                }
        }

        display( obj, metadata=metadata, raw=True )