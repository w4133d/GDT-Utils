"""
## XAsset Module, v0.3 beta - prov3ntus

Python utility module defining objects of assets in APE, as well as the GDT itself.

Enables you to write/pull assets to/from GDTs, streamlining GDT automation in python.

Currently supported XAssets:
- XMaterials
- XImages

\- pv
"""

import os, sys
from utils import engine
from utils.engine import *

BO3_ROOT_NAME = 'Call of Duty Black Ops III'

def mw4_get_semantic( _hex: str ):
	"""
	Gets the scemantic type from 
	"""
	if( _hex.startswith( 'unk_semantic_' ) ):
		_hex = _hex.removeprefix( 'unk_semantic_' )
	
	return mw4_Semantics[ _hex ]

# Finish me if you ever decide to do full mw2019 supp
mw4_Semantics = {
	'0x0' : 'c&s',
	'0x1' : 'c&s',
	'0x2' : 'c&s',
	'0x9' : '',
	'0xA' : '',
	'0xB' : '',
	'0x1C' : '',
	'0x1D' : '',
	'0x3B' : '',
	'0x3C' : '',
	'0x3D' : '',
	'0x7B' : '',
	'0x7C' : ''
}



# PARENT
class XAsset():

	AssetTypes = {
	"material"	: 'material.gdf',
	"image" 	: 'image.gdf',
	"mtl"   	: 'material.gdf',
	"anim"  	: 'xanim.gdf',
	"xanim"  	: 'xanim.gdf',
	"model" 	: 'xmodel.gdf',
	"xmodel" 	: 'xmodel.gdf'
	}

	def __init__( self, asset_name: str, asset_type: str ) -> None:
		"""
		Contains common variables for XAssets, used as a parent class.

		(You can ignore this object)
		"""
		self.name = asset_name
		self.type = XAsset.AssetTypes[ asset_type ]



# XMODEL
class XModel( XAsset ):

	LODs = {
		0 : "filename",
		1 : "mediumLod",
		2 : "lowLod",
		3 : "lowestLod",
		4 : "lod4File",
		5 : "lod5File",
		6 : "lod6File",
		7 : "lod7File"
	}

	def __init__( self, xmodel_name: str, lod_paths_array: list[ str:7 ] ) -> None:
		"""
		# UNFINISHED

		(Had to do XMaterial first)
		"""
		super().__init__( xmodel_name, 'model' )

		self.LODs = {};

		for idx in range( len( lod_paths_array ) ):
			self.LODs[ XModel.LODs[ idx ] ] = lod_paths_array[ idx ];

		# Let's say lod_paths_array only has 3 LOD paths in. 
		# We would still need to define the other 5 LODs, even if they're empty
		for idx in range( 8 - len( lod_paths_array[ :8 ] ) ):
			self.LODs[ XModel.LODs[ idx * -1 ] ] = '';
		
		

	def GenerateGDTAsset( self ) -> list[ str ]:
		# You'll need to add in a .gdf template to the templates folder for xmodels, then add formatting (see image.gdf)
		pass



# XIMAGE
class XImage( XAsset ):

	Semantics = {
		'default' : '2d',
		'_c' : 'diffuseMap',
		'_g' : 'glossMap',
		'_n' : 'normalMap',
		'_o' : 'occlusionMap',
		'_r' : 'revealMap',
		'_s' : 'specularMap' # specMap has colour, specMask doesn't
	}

	def GetCompressionMethod( semantic: str ) -> tuple:
		"""
		Returns a tuple of compression methods available for that semantic type

		(Just use the 1st index in most cases)
		"""
		if semantic == 'diffuseMap':
			return ( 'compressed high color', 'compressed low color', 'compressed no alpha', 'uncompressed' )
		
		return ( 'compressed', 'uncompressed' )

	def __init__( self, image_name: str = '', file_path: str = '' ) -> None:
		"""
		### @params:

		image_name | What the image will actually be called in APE, e.g. "i_pv_brushed_metal_c"\n
		(ideally, you want "image_name" to just be the file name, so you can keep files organised. Upon __init__, the "i_" will be appended if not already present.)

		file_path | The path to the image file.

		Note: XImage uses the file's name to determine semantic type (colorMap, normalMap, glossMap, etc.).
		Please ensure that the image's file name is suffixed correctly (e.g. "bricks_worn_white_c" AND NOT "bricks_worn_white")

		XImage will default to the semantic "2d" (like APE does) if there is no suffix.
		"""
		if( not image_name.startswith( 'i_' ) and image_name != '' ):
			image_name = 'i_' + image_name

		super().__init__( image_name, 'image' )
		self.path = file_path
		self.pbr_type = None

		if( image_name == '' ):
			return

		# DETERMINE SEMANTIC
		# 1. Attempt to look for mtl_images.txt that comes in the _images folder (it's not in the images folder lol tf was i thinking about)
		"""
		print( level.mtl_text_files_dir )
		_mtl_file = engine.GetFilesInDir( level.mtl_text_files_dir, full_path=True, extention='.txt', include_dirs=False )
		if( not len( _mtl_file ) ):
			RaiseError( 'Greyhound's images.txt files could not be found in chosen directory' )
			raise FileNotFoundError( 'There are no .txt files in the mtl_images.txt directory. Please make sure you\'ve chosen the right directory, and try agian.' )
		self.pbr_type = engine.SearchFileForKeyword( _mtl_file[0], self.name, all=False ).split( ',' )[0] # Needs finishing to account for unk_semantics
		"""

		# 2. Fallback - Determine semantic type based on suffix of the 
		# image file name e.g. "wooden_barrier_c.png" is an albedo map, 
		# but check for combo maps, like color&spec~012345.png maps
		if( self.pbr_type is None ):
			_file_name = engine.GetBaseName( self.path )
			self.pbr_type = XImage.Semantics[ 'default' ] # Default to 2d if there is no underscore at the end of the file name

			_suffix = '_' + _file_name.split( '_' )[ -1 ]
			try:
				self.pbr_type = XImage.Semantics[ _suffix ]
			except KeyError as e:
				RaiseWarning( 'asset.py -> class XImage -> __init__(): Defaulting XImage', _file_name + '.png', f'to 2d - Unrecognised suffix "{_suffix}"' )

			for _suffix, _type in XImage.Semantics:

				if( _file_name.endswith( _suffix ) ):
					self.pbr_type = _type
					break
	

	def GenerateGDTAsset( self ) -> list[ str ]:
		with open( f'utils\\gdt\\templates\\{ self.type }' ) as f:
			data = f.read()
		
		return data.format(
			_asset_name=self.name,
			_file_path=self.path.split( BO3_ROOT_NAME + '/' )[1],
			_pbr_type=self.pbr_type,
			_compression=XImage.GetCompressionMethod( self.pbr_type )[0]
		)



# XMATERIAL
class XMaterial( XAsset ):

	SURFACE_TYPES = (
		"<none>", "asphalt", "brick", "carpet", "ceramic", "cloth", "concrete", "dirt", "flesh", "foliage", "glass", "grass",
		"gravel", "ice", "metal", "mud", "paper", "plaster", "plastic", "rock", "rubber", "sand", "snow", "water", "wood",
		"cushion", "fruit", "paintedmetal", "tallgrass", "riotshield", "bark", "player", "metalthin", "metalhollow",
		"metalcatwalk", "metalcar", "glasscar", "glassbulletproof", "watershallow", "bodyarmor"
	);

	GLOSS_SURFACE_TYPES = (

	);

	def __init__( self, mtl_name: str = "", _ximages: list[ XImage ] = None, mtl_category: str = 'Geometry', mtl_type: str = 'lit', surface_type: str = '<none>', gloss_range: str = '<full>' ) -> None:
		"""
### @params:
		
mtl_name		| The name of the material asset\n
_ximages		| An array of XImage assets that belong to the XMtl\n
mtl_category	| E.g. "Geometry", "Geometry Advanced", "2d", "Weapons", etc.\n
mtl_type		| Deps. on mtl_category. E.g. "lit", "lit_plus", "lit_emissive", "lit_alphatest_advanced_fullspec", etc.\n
surface_type	| List of surface types (for reference):
- <none> // Default
- asphalt
- brick
- carpet
- ceramic
- cloth
- concrete
- dirt
- flesh
- foliage
- glass
- grass
- gravel
- ice
- metal
- mud
- paper
- plaster
- plastic
- rock
- rubber
- sand
- snow
- water
- wood
- cushion
- fruit
- paintedmetal
- tallgrass
- riotshield
- bark
- player
- metalthin
- metalhollow
- metalcatwalk
- metalcar
- glasscar
- glassbulletproof
- watershallow
- bodyarmor

gloss_range | List of gloss ranges (for reference):
- <custom>
- <full>
- asphalt
- brick
- carpet
- ceramic
- cloth
- concrete
- dirt
- skin
- foliage
- glass
- gravel
- ice
- metal
- mud
- paint
- paper
- plaster
- plastic
- rock
- rubber
- sand
- snow
- water
- wood
- bark
		"""
		super().__init__( mtl_name, 'mtl' );

		self.mtl_category = mtl_category;
		self.surface_type = surface_type;
		self.gloss_range = gloss_range;
		self.mtl_type = mtl_type;

		self.ximages = {
			'revealMap' 	: XImage(),
			'diffuseMap' 	: XImage(),
			'glossMap' 		: XImage(),
			'normalMap' 	: XImage(),
			'occlusionMap' 	: XImage(),
			'specularMap' 	: XImage()
		};
		for _ximg in _ximages:
			self.ximages[ _ximg.pbr_type ] = _ximg;
			
			if _ximg.pbr_type in ( 'glossMap', 'occlusionMap' ):
				self.mtl_category = 'Geometry Plus';

			if _ximg.pbr_type in ( 'specularMap', 'specularMask' ):
				self.mtl_category = 'Geometry Advanced';



	def GenerateGDTAsset( self ) -> list[ str ]:
		with open( f'utils\\gdt\\templates\\{self.type}' ) as f:
			data = f.read()
		
		# Texture maps
		_reveal = self.ximages[ "revealMap" 	].name;
		_color 	= self.ximages[ "diffuseMap" 	].name;
		_gloss 	= self.ximages[ "glossMap" 		].name;
		_normal = self.ximages[ "normalMap" 	].name;
		_occlu	= self.ximages[ "occlusionMap" 	].name;
		_spec	= self.ximages[ "specularMap" 	].name;

		# Misc info
		_surface_type	= self.surface_type;
		_gloss_range	= self.gloss_range;
		_mtl_category	= self.mtl_category;
		_mtl_type		= self.mtl_type;

		return data.format(
			_asset_name	= self.name,
			reveal_map	= _reveal,
			col_map		= _color,
			gloss_map	= _gloss,
			normal_map	= _normal,
			ao_map		= _occlu,
			spec_map	= _spec,
			srfc_type	= _surface_type,
			gloss_range	= _gloss_range,
			category	= _mtl_category,
			mtl_type	= _mtl_type,
		)



# GDT FILE
class GDT():

	def __init__( self, _gdt_path: str ) -> None:
		"""
		Object that represents a GDT file.

		Has various utility functions. 

		Please ensure you use self.CloseGDT || self.save_gdt() when you've 
		finished editing the GDT. 
		
		This is because GDT needs to put pack the closing curly bracket at the end 
		of the GDT file it removed when called for ease of adding XAssets to it.

		### @params:
		
		_gdt_path | You must give a full file path, no cwd shit.
		"""
		
		self.n_asset_count = 0;
		
		if engine.GetFileExtention( _gdt_path ) != '.gdt':
			_gdt_path += os.path.join( engine.GetDirName( _gdt_path ), engine.GetBaseName( _gdt_path ) + '.gdt')
		
		self.path = _gdt_path
		
		# Check if it's empty, get asset count & remove trailing whitespace
		with open( self.path, 'r' ) as f:
			data = f.read()

		if os.path.exists( self.path ) and not (engine.StripAll( data, '\n', '\t', ' ', '{', '}' ) == ''):
			with open( self.path, 'r' ) as self.file:
				lines = self.file.readlines()
				self.n_asset_count = lines.count( '{' ) - 1 if len( lines ) > 0 else 0

				while lines[ -1 ] == '\n':
					lines = lines[ :-1]  # remove all empty lines
				lines = lines[ :-1 ] # remove the } at the end of the GDT in memory
			
			with open( self.path, 'w' ) as self.file:
				self.file.writelines( lines )
		else: # Wipes the file if it has no assets in, and starts writing to it
			with open( self.path, 'w' ) as f:
				f.write( '{\n' )
	

	
	def IsEmpty( self ):
		#return true if engine.StripAll( self.file.read(), '\n', '\t', ' ' ) in ( '{}', '' ) else false
		return true if not self.n_asset_count else false

	def GetAsset( self, asset_name: str ) -> XImage | XModel | dict:
		pass

	def GetAssetRaw( self, asset_name: str ) -> list[ str ]:
		"""
		Returns the raw data of the asset from the GDT for copying assets 
		to / from GDTs, or for when they have properties unsupported by the 
		utils that need to be preserved.

		Returns an empty list if the asset doesn't exist in the GDT.
		"""

		if( not self.asset_exists( asset_name ) ):
			RaiseWarning( f'Could not find asset "{asset_name}" in GDT file "{GetBaseName( self.path )}"' );
			return [];

		with open( self.path, 'r' ) as self.file:
			raw_data = self.file.read();
		
		# Slice gdt str from where it finds the asset to where it finds the next '}' after
		start_idx = raw_data.find( f'"{asset_name}" (' )
		start_idx = start_idx if start_idx != -1 else raw_data.find( f'"{asset_name}" [' )
		raw_data = raw_data[ start_idx: ]
		raw_data = raw_data[ :raw_data.find( '}' ) + 1 ]

		return raw_data;

	def get_asset_count( self ):
		return self.n_asset_count

	def asset_exists( self, asset: XModel | XImage | str ):
		"""
		Returns true if the asset exists in the GDT
		"""

		if type( asset ) == XImage or type( asset ) == XModel:
			_search_kwds = ( f'"{asset.name}" ( "{asset.type}.gdf" )', f'"{asset.name}" [' )
		else:
			_search_kwds = ( f'"{asset}" (', f'"{asset}" [' )
		
		with open( self.path, 'r' ) as self.file:
			for _str in _search_kwds:
				if self.file.read().find( _str ) != -1:
					return True
		
		return False
	
	def HasAsset( self, asset: XModel | XImage | str ):
		"""
		Returns true if the asset exists in the GDT
		"""
		return self.asset_exists( asset )
	

	
	def NewAsset( self, asset: XImage | XModel ) -> None:
		"""
		Creates a new asset in the GDT (same as right clicking in APE & pressing 'New Asset')

		### @params:

		asset = an XAsset to be written to the GDT
		"""

		if self.asset_exists( asset ):
			engine.RaiseWarning( f"Tried to create {asset.type} asset {asset.name}, but an asset with that name already exists. Skipping..." )
			return;

		self.file.write( asset.GenerateGDTAsset() )
		self.file.write( '\n' )
		self.n_asset_count += 1

	
	def WriteAsset( self, asset: XImage | XModel ) -> None:
		"""
		Creates a new asset in the GDT (same as right clicking in APE & pressing 'New Asset')

		### @params:

		asset = an XAsset to be written to the GDT
		"""
		self.NewAsset( asset )
	
	def save_gdt( self ) -> None:
		self.CloseGDT()
	
	def CloseGDT( self ) -> None:
		
		with open( self.path, 'r' ) as self.file:
			file_data = self.file.read()

		if( file_data.strip() == '' ):
			return

		with open( self.path, 'r' ) as f:
			file_data = f.readlines()

		while file_data[ -1 ] == '\n':
			file_data = file_data

		if( not file_data[ -1 ] == '}' ):
			file_data += '}'
		
		file_data += '\n'
		with open( self.path, 'w' ) as self.file:
			self.file.writelines( file_data )





__all__ = [ 'XImage', 'XMaterial', 'XModel', 'GDT', 'mw4_get_semantic' ]




