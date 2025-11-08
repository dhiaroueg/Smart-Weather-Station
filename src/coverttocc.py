# make_model_cc.py
data = open("model.tflite", "rb").read()
with open("model.cc", "w") as f:
    f.write("unsigned char model_tflite[] = {")
    f.write(",".join(str(b) for b in data))
    f.write("};\nunsigned int model_tflite_len = %d;" % len(data))
print("Generated model.cc with", len(data), "bytes")
