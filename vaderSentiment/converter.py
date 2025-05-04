import csv, os, zipfile
from lxml import etree

def sentiment_color(sentiment):
    return {
        "positive": "#00ff00",
        "negative": "#ff0000",
        "neutral": "#aaaaaa"
    }.get(sentiment, "#cccccc")

def create_entity_xml(entity_id, entity_type, value, sentiment, compound):
    entity = etree.Element("Entity")
    entity.set("EntityType", entity_type)
    entity.set("Version", "0.1")

    props = etree.SubElement(entity, "Properties")
    etree.SubElement(props, "Property", Name="maltego.entity.value", Value=value)
    etree.SubElement(props, "Property", Name="Sentiment", Value=sentiment)
    etree.SubElement(props, "Property", Name="CompoundScore", Value=str(compound))

    vis = etree.SubElement(entity, "VisualizationInfo")
    etree.SubElement(vis, "Label", Value=value)
    etree.SubElement(vis, "Color", BackgroundColor=sentiment_color(sentiment))

    return entity

def build_graph(entities):
    root = etree.Element("MaltegoGraph")
    entities_node = etree.SubElement(root, "Entities")
    for e in entities:
        entities_node.append(e)
    return etree.tostring(root, pretty_print=True)

def generate_mtgx(csv_path, output_path):
    entities = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            ent = create_entity_xml(
                # for each column in the CSV, create an entity
                # and set the properties accordingly
                entity_id=f"e{i}",
                entity_type=row["Type"],
                value=row["Entity"],
                sentiment=row["Sentiment"],
                compound=row["Compound"]
            )
            entities.append(ent)

    xml_data = build_graph(entities)

    os.makedirs("tmp_mtgx", exist_ok=True)
    with open("tmp_mtgx/graph.graph", "wb") as f:
        f.write(xml_data)

    with zipfile.ZipFile(output_path, 'w') as zipf:
        zipf.write("tmp_mtgx/graph.graph", arcname="graph.graph")

    print(f"MTGX file created: {output_path}")

# Usage
generate_mtgx("output.csv", "sentiment_graph.mtgx")
