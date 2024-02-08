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
    Recommendation: URIRef
    Metric: URIRef
    Visualization: URIRef
    RealtimeDataVisualization: URIRef
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
    hasTimeRange: URIRef
    hasRecommendationScore: Literal
    hasPosition: Literal

    # Recommender Model
    version: Literal

    # Property
    produces: URIRef

    # Visualization
    accepts: URIRef

    # ObservationBoundary
    hasMinBoundary: Literal
    hasMaxBoundary: Literal
    hasBoundaryLabel: Literal

    # TimeRange
    hasDuration: Literal
    fromTimeRange: Literal
    toTimeRange: Literal

    _NS = Namespace('http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#')
