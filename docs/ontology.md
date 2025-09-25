# Ontology

## Predicates

| Predicate | Definition |
|---|---|
| IS_A | Denotes a class-or-type relationship between two entities (e.g., 'Model Y IS_A electric-SUV'). Includes 'is' and 'was'. |
| HAS_A | Denotes a part-whole relationship between two entities (e.g., 'Model Y HAS_A electric-engine'). Includes 'has' and 'had'. |
| LOCATED_IN | Specifies geographic or organisational containment or proximity (e.g., headquarters LOCATED_IN Berlin). |
| HOLDS_ROLE | Connects a person to a formal office or title within an organisation (CEO, Chair, Director, etc.). |
| PRODUCES | Indicates that an entity manufactures, builds, or creates a product, service, or infrastructure (includes scale-ups and component inclusion). |
| SELLS | Marks a commercial seller-to-customer relationship for a product or service (markets, distributes, sells). |
| LAUNCHED | Captures the official first release, shipment, or public start of a product, service, or initiative. |
| DEVELOPED | Shows design, R&D, or innovation origin of a technology, product, or capability. Includes 'researched' or 'created'. |
| ADOPTED_BY | Indicates that a technology or product has been taken up, deployed, or implemented by another entity. |
| INVESTS_IN | Represents the flow of capital or resources from one entity into another (equity, funding rounds, strategic investment). |
| COLLABORATES_WITH | Generic partnership, alliance, joint venture, or licensing relationship between entities. |
| SUPPLIES | Captures vendor–client supply-chain links or dependencies (provides to, sources from). |
| HAS_REVENUE | Associates an entity with a revenue amount or metric—actual, reported, or projected. |
| INCREASED | Expresses an upward change in a metric (revenue, market share, output) relative to a prior period or baseline. |
| DECREASED | Expresses a downward change in a metric relative to a prior period or baseline. |
| RESULTED_IN | Captures a causal relationship where one event or factor leads to a specific outcome (positive or negative). |
| TARGETS | Denotes a strategic objective, market segment, or customer group that an entity seeks to reach. |
| PART_OF | Expresses hierarchical membership or subset relationships (division, subsidiary, managed by, belongs to). |
| DISCONTINUED | Indicates official end-of-life, shutdown, or termination of a product, service, or relationship. |
| SECURED | Marks the successful acquisition of funding, contracts, assets, or rights by an entity. |
| MENTIONS | Denotes a reference or mention of an entity in a text or document. |
| FEELS | Denotes a subjective opinion or feeling about an entity (e.g., 'I feel like X').Includes 'THINKS'. |
| HELPS | Express a action that make it easier or possible for (someone) to do something by offering one's services or resources. Includes 'assist', 'aid' and 'support' . |
| IS_DOING | Denotes a subjective action or activity about an entity (e.g., 'I am doing X').Includes 'DOES'. |
| LIKES | Express enjoy or approve of something or someone (e.g., 'I like roses').Includes 'LIKES'. |
| DISLIKES | Express dislike or disapprove of something or someone (e.g., 'I dislike roses').Includes 'DISLIKES'. |

## Labels

### Episode Labelling

| Label | Definition | Date Handling Guidance | Date Handling Example |
|---|---|---|---|
| FACT | Statements that are objective and can be independently verified or falsified through evidence. | These statements can be made up of multiple static and dynamic temporal events marking for example the start, end, and duration of the fact described statement. | 'Company A owns Company B in 2022', 'X caused Y to happen', or 'John said X at Event' are verifiable facts which currently hold true unless we have a contradictory fact. |
| OPINION | Statements that contain personal opinions, feelings, values, or judgments that are not independently verifiable. It also includes hypothetical and speculative statements. | This statement is always static. It is a record of the date the opinion was made. | 'I like Company A\'s strategy', 'X may have caused Y to happen', or 'The event felt like X' are opinions and down to the reporters interpretation. |
| PREDICTION | Uncertain statements about the future on something that might happen, a hypothetical outcome, unverified claims. It includes interpretations and suggestions. If the tense of the statement changed, the statement would then become a fact. | This statement is always static. It is a record of the date the prediction was made. | 'It is rumoured that Dave will resign next month', 'Company A expects X to happen', or 'X suggests Y' are all predictions. |

### Temporal Labelling

| Label | Definition | Date Handling Guidance | Date Handling Example |
|---|---|---|---|
| STATIC | Often past tense, think -ed verbs, describing single points-in-time. These statements are valid from the day they occurred and are never invalid. Refer to single points in time at which an event occurred, the fact X occurred on that date will always hold true. | The valid_at date is the date the event occurred. The invalid_at date is None. | 'John was appointed CEO on 4th Jan 2024', 'Company A reported X percent growth from last FY', or 'X resulted in Y to happen' are valid the day they occurred and are never invalid. |
| DYNAMIC | Often present tense, think -ing verbs, describing a period of time. These statements are valid for a specific period of time and are usually invalidated by a Static fact marking the end of the event or start of a contradictory new one. The statement could already be referring to a discrete time period (invalid) or may be an ongoing relationship (not yet invalid). | The valid_at date is the date the event started. The invalid_at date is the date the event or relationship ended, for ongoing events this is None. | 'John is the CEO', 'Company A remains a market leader', or 'X is continuously causing Y to decrease' are valid from when the event started and are invalidated by a new event. |
| ATEMPORAL | Statements that will always hold true regardless of time therefore have no temporal bounds. | These statements are assumed to be atemporal and have no temporal bounds. Both their valid_at and invalid_at are None. | 'A stock represents a unit of ownership in a company', 'The earth is round', or 'Europe is a continent'. These statements are true regardless of time. |