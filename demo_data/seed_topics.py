"""Create demo topics in Kafka cluster."""
import os
import time
from confluent_kafka.admin import AdminClient, NewTopic


def wait_for_kafka(admin_client, max_retries=30, delay=2):
    """Wait for Kafka to be ready."""
    print("Waiting for Kafka to be ready...")
    for i in range(max_retries):
        try:
            metadata = admin_client.list_topics(timeout=5)
            print(f"Kafka is ready! Found {len(metadata.topics)} existing topics.")
            return True
        except Exception as e:
            print(f"Attempt {i+1}/{max_retries}: Kafka not ready yet ({e})")
            time.sleep(delay)
    return False


def create_topics():
    """Create demo topics in Kafka."""
    # Get Kafka connection from environment
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

    print(f"Connecting to Kafka at {bootstrap_servers}...")

    # Create AdminClient
    admin_client = AdminClient({
        "bootstrap.servers": bootstrap_servers
    })

    # Wait for Kafka to be ready
    if not wait_for_kafka(admin_client):
        print("ERROR: Kafka is not ready after waiting. Exiting.")
        return

    # Define demo topics
    topics = [
        NewTopic("user-events", num_partitions=2, replication_factor=1),
        NewTopic("system-logs", num_partitions=1, replication_factor=1),
        NewTopic("order-processing", num_partitions=2, replication_factor=1),
    ]

    print(f"\nCreating {len(topics)} demo topics...")

    # Create topics
    fs = admin_client.create_topics(topics)

    # Wait for topic creation to complete
    for topic, f in fs.items():
        try:
            f.result()  # The result itself is None
            print(f"✓ Topic '{topic}' created successfully")
        except Exception as e:
            # Topic might already exist, which is fine
            if "already exists" in str(e).lower():
                print(f"✓ Topic '{topic}' already exists")
            else:
                print(f"✗ Failed to create topic '{topic}': {e}")

    print("\nDemo topics setup complete!")

    # List all topics to verify
    metadata = admin_client.list_topics(timeout=10)
    print(f"\nTotal topics in cluster: {len(metadata.topics)}")
    print("Topics:")
    for topic_name in sorted(metadata.topics.keys()):
        if not topic_name.startswith("_"):  # Skip internal topics
            print(f"  - {topic_name}")


if __name__ == "__main__":
    create_topics()
