from rdflib.term import Literal, URIRef
from rdflib.namespace import DefinedNamespace, Namespace


class DASHB(DefinedNamespace):
    """
    The Dynamic Dashboard Ontology
    """

    _fail = True

    # Classes
    User: URIRef
    UserGroup: URIRef
    Dashboard: URIRef
    Tab: URIRef
    Widget: URIRef
    Property: URIRef
    Metric: URIRef
    Visualization: URIRef
    ObservationBoundary: URIRef

    # User
    memberOf: URIRef

    # Dashboard
    hasTab: URIRef

    # Tab
    hasWidget: URIRef

    # Widget
    createdBy: URIRef
    hasProperty: URIRef
    visualizedBy: URIRef
    hasObservationBoundary: URIRef

    # Property
    produces: URIRef

    # ObservationBoundary
    hasMinBoundary: Literal
    hasMaxBoundary: Literal
    hasBoundaryLabel: Literal

    _NS = Namespace('https://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#')
