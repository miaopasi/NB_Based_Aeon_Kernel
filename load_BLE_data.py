__author__ = 'Xiaolong Shen @ NexdTech'
import os
from numpy import *


class MatResult:
	"""
		res.mat : Matrix of All Samples
		res.cls : Class Label of All Samples
		res.cls_ref : Ref of filename of each Class
						{ filename : class }
		res.sep_mat : Dictionary containing each file into one matrix
						{ filename : Matrix of this file }
		res.coord_flag : True/False to determine whether coordinates contained in the data
		res.cls_coord : The coordinate of each class for exact accuracy. Is not empty when res.coord_flag is True.
	"""
	def __init__(self):
		self.mat = []
		self.sep_mat = {}
		self.cls = []
		self.cls_ref = {}
		self.coord_flag = False
		self.cls_coord = {}


class LoadData:
	"""
		Load In BlueTooth Collected Data
		Need Input data dirpath.
			Input Data Format:
				// Header
				UUID Major Minor RSSI Time
				# TimeStamp SampleNumber
				UUID Major Minor RSSI Time
				# TimeStamp SampleNumber
				...
				UUID Major Minor RSSI Time
				# TimeStamp SampleNumber

		Optional:
			Coordinate File Path
				Coord File Format:
					filename posx posy
					filename posx posy
					...
					filename posx posy

	"""
	def __init__(self, dir_path=None, coord_path=None, marker_dict=None):
		if dir_path is not None:
			self.data_path = dir_path
			self.load_res = self._load(dir_path)
			self.mat_res = self._reorg(self.load_res, marker_dict)
			self.mat_res.mat = asarray(self.mat_res.mat)
			for filename in self.mat_res.sep_mat:
				self.mat_res.sep_mat[filename] = asarray(self.mat_res.sep_mat[filename])
			self.mat_res.cls = asarray(self.mat_res.cls)
		else:
			assert "No DirPath. Failed Loading Data."
			print "No DirPath. Failed Loading Data."
		if coord_path is not None:
			self.mat_res.coord_flag = True
			self.mat_res.cls_coord = self._get_coord(coord_path)
			pass
		else:
			assert "No CoordPath. Failed Loading Pos."
			print "No CoordPath. Failed Loading Pos."

	def _get_coord(self, coord_path):
		cord_res = {}
		f = open(coord_path)
		for line in f:
			ls = line.split()
			if len(ls) == 3:
				cord_res[int(ls[0])] = [float(ls[1]),float(ls[2])]
		f.close()
		return cord_res


	def _reorg(self, load_res, marker_dict=None):
		"""
		Reorganize Data into Matrix Format;

		:param load_res: Dictionary format result of load
		:return res: Matrix Format Results, major-minor marker string, Defined by Class MatResult
					res.mat : Matrix of All Samples
					res.cls : Class Label of All Samples
					res.cls_ref : Ref of filename of each Class
									{ filename : class }
					res.sep_mat : Dictionary containing each file into one matrix
									{ filename : Matrix of this file }
					res.coord_flag : True/False to determine whether coordinates contained in the data
					res.cls_coord : The coordinate of each class for exact accuracy. Is not empty when res.coord_flag is True.
		"""
		# Build major-minor marker dict
		if marker_dict is None:
			marker_dict = []
			for filename in load_res:
				for sample in load_res[filename]:
					marker_dict = list(set(marker_dict + load_res[filename][sample].keys()))
		marker_len = len(marker_dict)
		res = MatResult()
		for filename in load_res:
			if filename in res.cls_ref:
				cls = res.cls_ref[filename]
			else:
				cls = filename
				res.cls_ref[filename] = cls
			res.sep_mat[filename] = []
			for sample in load_res[filename]:
				t_line = [0] * marker_len
				for marker in load_res[filename][sample]:
					ind = marker_dict.index(marker)
					t_line[ind] = load_res[filename][sample][marker]
				res.mat.append(t_line)
				res.cls.append(cls)
				res.sep_mat[filename].append(t_line)
		self.marker_dict = marker_dict
		return res

	def _load_file(self, filename):
		"""
		Load Files And Store Results in Dictionary.

		:param filename: Name of Loading Files
		:return res: Dictionary {
									samples:
										{ "major-minor" : Signal Strength
										}
								}
		"""
		res = {}
		t_res = {}
		f = open(filename)
		for line in f:
			if '//' in line:
				# Header Information
				continue
			if '#' in line:
				# End of One Sample Block
				ls = line.split()
				res[ls[2]] = dict(t_res)
				t_res = {}
				continue
			ls = line.split()
			major_minor_str = "-".join([ls[1], ls[2]])
			t_res[major_minor_str] = int(ls[3])
		f.close()
		return res

	def _load(self, data_path):
		file_list = os.listdir(data_path)
		load_res = {}
		for filename in file_list:
			name, ext = os.path.splitext(filename)
			if 'txt' in ext:
				try:
					dict_name = int(name.split('-')[1]) - 1
				except Exception,e:
					print "name load fail %s" %(name)

					dict_name = name
				load_res[dict_name] = self._load_file(os.path.join(data_path, filename))
		return load_res

