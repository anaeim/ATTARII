def remove_unicode_chars(string_unicode):
	string_encode = string_unicode.encode("ascii", "ignore")
	string_decode = string_encode.decode()
	
	return string_decode
