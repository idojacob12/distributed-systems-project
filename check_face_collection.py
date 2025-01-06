import boto3

def list_faces_in_collection(collection_id):
    # Create a Rekognition client
    rekognition = boto3.client('rekognition', region_name='us-east-1')

    # List faces in the collection
    response = rekognition.list_faces(
        CollectionId=collection_id,
        MaxResults=20
    )

    # Print information about the faces in the collection
    if 'Faces' in response:
        print(f"Found {len(response['Faces'])} faces in the collection.")
        for face in response['Faces']:
            print(f"FaceId: {face['FaceId']}")
            print(f"ExternalImageId: {face.get('ExternalImageId', 'No ExternalImageId assigned')}")
            print(f"Confidence: {face['Confidence']}%")
            print("------")
    else:
        print("No faces found in the collection.")


collection_id = 'known_faces_collection'  # The ID of your collection
list_faces_in_collection(collection_id)