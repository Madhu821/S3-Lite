import os
import hashlib

CHUNK_SIZE = 1024 * 1024 #1MB

def clean_old_metadata(file_name):
    if not os.path.exists("metadata.txt"):
        return

    with open("metadata.txt", "r") as meta:
        lines = meta.readlines()

    with open("metadata.txt", "w") as meta:
        for line in lines:
            if not line.startswith(file_name + ","):
                meta.write(line)

# split_file_into_chunks: Reads the file in chunks and stores them separately, while also maintaining metadata for reconstruction.

def slpit_file_into_chunks(file_path):
    file_name = os.path.basename(file_path)
    clean_old_metadata(file_name)


    with open(file_path, 'rb') as f:
        chunk_number = 0

        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break

            chunk_file_name = f"storage/{file_name}_chunk{chunk_number}"
            with open(chunk_file_name, 'wb') as chunk_file:
                chunk_file.write(data)
            
            chunk_hash = hashlib.sha256(data).hexdigest()
            with open("metadata.txt", 'a') as meta:
                meta.write(f"{file_name},{chunk_number},{file_name}_chunk{chunk_number},{chunk_hash}\n")

            print(f"Stored: {chunk_file_name}")
            chunk_number += 1


def reconstruct_file(original_file_name, output_file_name):
    with open(output_file_name, 'wb') as output_file:
        with open("metadata.txt", 'r') as meta:
            lines = meta.readlines()

            for line in lines:
                file, order, chunk_name, stored_hash = [x.strip() for x in line.strip().split(',')]

                if file == original_file_name:
                    chunk_path = f"storage/{chunk_name}"

                    with open(chunk_path, 'rb') as chunk_file:
                        data = chunk_file.read()

                        #Verify hash
                        current_hash = hashlib.sha256(data).hexdigest()
                        if current_hash != stored_hash:
                            print(f"Data Corrupted in {chunk_name}")
                            return
                    
                        output_file.write(data)


                    print(f"Read: {chunk_path}")


print("File Reconstructed Successfully.")


choice = input("Enter 1 to Upload, 2 to Reconstruct: ")

file_path = input("Enter the path file: ").strip('"')
file_name = os.path.basename(file_path)

if choice == "1":
    slpit_file_into_chunks(file_path)

elif choice == "2":
    reconstruct_file(file_name, "reconstructed_" + file_name)
