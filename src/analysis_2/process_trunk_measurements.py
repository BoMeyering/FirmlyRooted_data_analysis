import os
import pandas as pd



def process_trunk_picos(filename: str):
	pass

def process_trunk_adair(filename: str):
	"""
	arguments:
	filename: str -> a path to the prop_adair trunk height measurement file

	returns a csv file of the processed heights with appropriate filenames and units
	"""

	def _col_cat(df_row):
		return df_row['row'].upper() + '_' + str(df_row['tree'])
	
	raw = pd.read_csv(filename)\
		.rename(columns={
			"Label": "sys_id",
			"Length": "trunk_height_cm"
			})

	raw[['NA', 'sys_id']] = raw['sys_id'].str.split(':', expand=True)
	raw[['sys_id', 'NA2']] = raw['sys_id'].str.split('_still', expand=True)
	raw[['row', 'tree', 'vid_num']] = raw['sys_id'].str.split('_', expand=True)
	
	raw['sys_id'] = raw.apply(_col_cat, axis=1)
	
	processed = raw[['sys_id', 'trunk_height_cm', 'vid_num']]
	processed['vid_str'] = processed['vid_num'].astype(str)
	processed = processed.loc[processed['vid_str'].isin(['None', '1'])]
	processed = processed[['sys_id', 'trunk_height_cm']]
	return processed

def process_pixel_depths(filename: str, scale_pixels: int, scale_cm: int=30):
	"""
	"""
	def _col_cat(df_row):
		return '17' + df_row['row']

	def _sys_id_cat(df_row):
		return df_row['row'] + '_' + df_row['tree']
	
	depths = pd.read_csv(filename)
	depths['cm'] = depths['pixel_depth']/scale_pixels*scale_cm
	depths['tree'] = depths['filename'].str.extract(r'^(\d{2})[EW]').astype(str)
	depths['row'] = depths['filename'].str.extract(r'^\d{2}([EW]{1})').astype(str)
	depths['row'] = depths.apply(_col_cat, axis=1).astype(str)
	depths['sys_id'] = depths.apply(_sys_id_cat, axis=1)

	depths_agg = depths[['sys_id', 'pixel_depth', 'cm']].groupby(['sys_id']).mean()\
		.rename(
			columns={
				"pixel_depth": "load_depth_px",
				"cm": "load_depth_cm"
			}
		)

	return depths_agg



if __name__ == '__main__':
	pass