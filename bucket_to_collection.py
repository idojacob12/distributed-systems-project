import boto3
import time

# AWS Rekognition and S3 clients
rekognition = boto3.client('rekognition', region_name='us-east-1')
s3_client = boto3.client('s3', region_name='us-east-1')

# S3 Bucket and collection name
bucket_name = 'known-people'
collection_id = 'known_faces_collection'

# Create the collection
def create_collection(collection_id):
    try:
        response = rekognition.create_collection(CollectionId=collection_id)
        print(f"Collection '{collection_id}' created successfully!")
        return response
    except rekognition.exceptions.ResourceAlreadyExistsException:
        print(f"Collection '{collection_id}' already exists.")
        return None

# Add faces to the collection from the S3 bucket
def index_faces_in_collection(bucket_name, collection_id):
    # List objects in the bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)

    if 'Contents' not in response:
        print("No objects found in the S3 bucket.")
        return

    # Loop through each image in the S3 bucket
    for obj in response['Contents']:
        image_key = obj['Key']
        print(f"Processing image: {image_key}")

        try:
            # Call Rekognition to detect faces in the image
            rekognition_response = rekognition.index_faces(
                CollectionId=collection_id,
                Image={'S3Object': {'Bucket': bucket_name, 'Name': image_key}},
                MaxFaces=5,
                QualityFilter='AUTO',
                DetectionAttributes=['ALL']
            )
            print(f"Faces indexed from {image_key}: {len(rekognition_response['FaceRecords'])} faces added.")
        except Exception as e:
            print(f"Error processing {image_key}: {e}")

# Main logic
def main():
    # Step 1: Create the collection (if it doesn't exist)
    create_collection(collection_id)

    # Step 2: Index faces from S3 bucket into the collection
    index_faces_in_collection(bucket_name, collection_id)


if __name__ == "__main__":
    main()