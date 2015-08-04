## Usage Description

若以Jython作为中间件接驳JAVA和Python，则直接调用**interface_server.py**文件，其中可调用的函数为：interface_server(string filepath)

具体定义可参考：
>
	"""
	:input_param: file_path for one collection
	:output_param: list of dictionaries
		dictionary:
			user_id: special id for user, STRING
			post_x: x coordinate of position, DOUBLE
			post_y: y coordinate of position, DOUBLE
			post_cred: credibility of position, DOUBLE
			timestamp: the time when the position is given, LONG
	"""