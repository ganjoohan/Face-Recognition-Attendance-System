import warnings
warnings.filterwarnings("ignore")

import os
#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

'''
0 = all messages are logged (default behavior)
1 = INFO messages are not printed
2 = INFO and WARNING messages are not printed
3 = INFO, WARNING, and ERROR messages are not printed
'''

from src.basemodels import Facenet, Facenet512, FbDeepFace, VGGFace, ArcFace, SFace

import tensorflow as tf
tf_version = int(tf.__version__.split(".")[0])
if tf_version == 2:
	import logging
	tf.get_logger().setLevel(logging.ERROR)

def build_model(model_name):

	"""
	This function builds a deepface model
	Parameters:
		model_name (string): face recognition or facial attribute model
			VGG-Face, Facenet, OpenFace, DeepFace, DeepID for face recognition

	Returns:
		built deepface model
	"""

	global model_obj #singleton design pattern

	models = {
		'Facenet': Facenet.loadModel, #Google researchers: (99.20%) [128 dimensions]
		'Facenet512': Facenet512.loadModel, #Google researchers: (99.65%) [512 dimensions]
		'VGG-Face': VGGFace.loadModel, #University of Oxford researchers: (98.78%)
		'DeepFace': FbDeepFace.loadModel, # Facebook researchers: (97.53%)
		'ArcFace': ArcFace.loadModel, #Imperial College London and InsightFace researchers: (99.40%)
		'SFace': SFace.load_model, #SFace: Sigmoid-Constrained Hypersphere Loss for Robust Face Recognition
	}

	if not "model_obj" in globals():
		model_obj = {}

	if not model_name in model_obj.keys():
		model = models.get(model_name)
		if model:
			model = model()
			model_obj[model_name] = model

		else:
			raise ValueError('Invalid model_name passed - {}'.format(model_name))

	return model_obj[model_name]


