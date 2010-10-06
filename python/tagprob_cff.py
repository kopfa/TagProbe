import FWCore.ParameterSet.Config as cms

process = cms.Process("TagProbe")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

# register TFileService
process.TFileService = cms.Service("TFileService",
    fileName = cms.string('tagprob.root')
)

#process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring(
   #'file:/afs/cern.ch/user/t/tjkim/public/forColin/pf2pat_iso.root',
#   '/store/data/Run2010A/Mu/RECO/v4/000/142/136/1A788144-289E-DF11-AC2A-001D09F2960F.root'
#    )
#)

process.load("PFAnalyses.TTbarDIL.Sources.MU.MC.Spring10.patTuple_Zmumu_cff")

process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True))

from PFAnalyses.CommonTools.Selectors.muonSelectorPSet_cff import muonSelectorPSet
muonId = muonSelectorPSet.clone()
muonId.dxy = 0.02
muonId.eta = 2.5
muonId.pt = 20 
from PFAnalyses.CommonTools.Selectors.muonIsoSelectorPSet_cff import muonIsoSelectorPSet
muonIso = muonIsoSelectorPSet.clone()

process.taggedMuons = cms.EDProducer(
    "KoMuonSelector",
    version = cms.untracked.int32( 4 ),
    muonLabel  = cms.InputTag("selectedPatMuonsPFlow"),
    beamSpotLabel = cms.InputTag("offlineBeamSpot"),
    muonIdSelector = muonId,
    muonIsoSelector = muonIso,
)

process.load("KoPFA.DiMuonAnalyzer.triggerMatch_cfi")
process.patMuonTriggerMatch.src = "taggedMuons"
process.triggeredPatMuons.src = "taggedMuons"
#PASS_HLT = "!triggerObjectMatchesByPath('%s').empty()" % ("HLT_Mu9",);

process.tagMuons = cms.EDFilter("PATMuonSelector",
    src = cms.InputTag("triggeredPatMuons"),
    cut = cms.string("")
)

process.PFMuons = cms.EDProducer(
    "KoMuonRefSelector",
    version = cms.untracked.int32( 0 ),
    muonLabel  = cms.InputTag("selectedPatMuonsPFlow"),
    beamSpotLabel = cms.InputTag("offlineBeamSpot"),
    muonIdSelector = muonId,
    muonIsoSelector = muonIso,
)

process.IDMuons = cms.EDProducer(
    "KoMuonRefSelector",
    version = cms.untracked.int32( 1 ),
    muonLabel  = cms.InputTag("selectedPatMuonsPFlow"),
    beamSpotLabel = cms.InputTag("offlineBeamSpot"),
    muonIdSelector = muonId,
    muonIsoSelector = muonIso,
)

process.IsoMuons = cms.EDProducer(
    "KoMuonRefSelector",
    version = cms.untracked.int32( 4 ),
    muonLabel  = cms.InputTag("selectedPatMuonsPFlow"),
    beamSpotLabel = cms.InputTag("offlineBeamSpot"),
    muonIdSelector = muonId,
    muonIsoSelector = muonIso,
)

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.load("Geometry.CommonDetUnit.globalTrackingGeometry_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAny_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorAlong_cfi")
process.load("TrackPropagation.SteppingHelixPropagator.SteppingHelixPropagatorOpposite_cfi")
process.GlobalTag.globaltag = cms.string('MC_3XY_V14::All')

process.goodTracks = cms.EDFilter("TrackSelector",
    src = cms.InputTag("generalTracks"), # or cms.InputTag("standAloneMuons","UpdatedAtVtx"), 
    cut = cms.string(""),
#    cut = cms.string("numberOfValidHits >= 10 && normalizedChi2 < 5 && abs(d0) < 2 && abs(dz) < 30"),
)
process.trackCands  = cms.EDProducer("ConcreteChargedCandidateProducer", 
    src  = cms.InputTag("goodTracks"),      
    particleType = cms.string("mu+"),     # this is needed to define a mass
)
process.trackProbes = cms.EDFilter("CandViewRefSelector",
    src = cms.InputTag("trackCands"),
    cut = cms.string("pt > 5"),
)

process.tkToPFMuons = cms.EDProducer("MatcherUsingTracks",
    src     = cms.InputTag("trackCands"), # all tracks are available for matching
    matched = cms.InputTag("PFMuons"), # to all global muons
    algorithm = cms.string("byDirectComparison"), # check that they
    srcTrack = cms.string("tracker"),             # have the same 
    srcState = cms.string("atVertex"),            # tracker track
    matchedTrack = cms.string("tracker"),         # can't check ref
    matchedState = cms.string("atVertex"),        # because of the
    maxDeltaR        = cms.double(0.01),          # embedding.
    maxDeltaLocalPos = cms.double(0.01),
    maxDeltaPtRel    = cms.double(0.01),
    sortBy           = cms.string("deltaR"),
)

process.passingprobesForPFMuons = cms.EDProducer("MatchedCandidateSelector",
    src   = cms.InputTag("trackProbes"),
    match = cms.InputTag("tkToPFMuons"),
)

process.tkToIDMuons = cms.EDProducer("MatcherUsingTracks",
    src     = cms.InputTag("trackCands"), # all tracks are available for matching
    matched = cms.InputTag("IDMuons"), # to all global muons
    algorithm = cms.string("byDirectComparison"), # check that they
    srcTrack = cms.string("tracker"),             # have the same 
    srcState = cms.string("atVertex"),            # tracker track
    matchedTrack = cms.string("tracker"),         # can't check ref
    matchedState = cms.string("atVertex"),        # because of the
    maxDeltaR        = cms.double(0.01),          # embedding.
    maxDeltaLocalPos = cms.double(0.01),
    maxDeltaPtRel    = cms.double(0.01),
    sortBy           = cms.string("deltaR"),
)

process.passingprobesForIDMuons = cms.EDProducer("MatchedCandidateSelector",
    src   = cms.InputTag("trackProbes"),
    match = cms.InputTag("tkToIDMuons"),
)


process.tagProbes = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("tagMuons@+ trackProbes@-"), # charge coniugate states are implied; 'tagMuons' and 'trkProbes' should be collections of Candidates
    cut   = cms.string("20 < mass < 200"),
)

process.tagProbesIso = cms.EDProducer("CandViewShallowCloneCombiner",
    decay = cms.string("tagMuons@+ IDMuons@-"), # charge coniugate states are implied; 'tagMuons' and 'trkProbes' should be collections of Candidates
    cut   = cms.string("20 < mass < 200"),
)

process.muMcMatchTag = cms.EDProducer("MCTruthDeltaRMatcherNew",
    pdgId = cms.vint32(13),
    src = cms.InputTag("tagMuons"),
    distMin = cms.double(0.3),
    matched = cms.InputTag("genParticles")
)

process.muMcMatchTrackProbe = cms.EDProducer("MCTruthDeltaRMatcherNew",
    pdgId = cms.vint32(13),
    src = cms.InputTag("trackCands"),
    distMin = cms.double(0.3),
    matched = cms.InputTag("genParticles")
)

process.muMcMatchIDMuonProbe = cms.EDProducer("MCTruthDeltaRMatcherNew",
    pdgId = cms.vint32(13),
    src = cms.InputTag("selectedPatMuonsPFlow"),
    distMin = cms.double(0.3),
    matched = cms.InputTag("genParticles")
)

process.tnpTree = cms.EDAnalyzer("TagProbeFitTreeProducer",
    # choice of tag and probe pairs, and arbitration
    tagProbePairs = cms.InputTag("tagProbes"),
    arbitration   = cms.string("OneProbe"), ## that is, use only tags associated to a single probe.
    # probe variables
    variables = cms.PSet(
        pt     = cms.string("pt"),
        abseta = cms.string("abs(eta)"),
    ),
    # choice of what defines a 'passing' probe
    flags = cms.PSet(
        #isIso = cms.string("(chargedHadronIso + neutralHadronIso/0.33 + photonIso)/pt < 0.21"),
        isPFMuon = cms.InputTag("passingprobesForPFMuons"),
        isIDMuon = cms.InputTag("passingprobesForIDMuons"),
        #isGlobalMuon = cms.string("isGlobalMuon"),
        #isHLTMu3     = cms.string("!triggerObjectMatchesByFilter('hltSingleMu3L3Filtered3').empty()"),  
    ),
    ## DATA-related info
    addRunLumiInfo = cms.bool(True),
    ## MC-related info
    isMC = cms.bool(False), ## on MC you can set this to true, add some parameters and get extra info in the tree.
    motherPdgId = cms.vint32(22,23),
    makeMCUnbiasTree = cms.bool(True),
    checkMotherInUnbiasEff = cms.bool(True),
    tagMatches = cms.InputTag("muMcMatchTag"),
    probeMatches  = cms.InputTag("muMcMatchTrackProbe"),
    allProbes     = cms.InputTag("trackProbes"),

)

process.tnpTreeIso = cms.EDAnalyzer("TagProbeFitTreeProducer",
    # choice of tag and probe pairs, and arbitration
    tagProbePairs = cms.InputTag("tagProbesIso"),
    arbitration   = cms.string("OneProbe"), ## that is, use only tags associated to a single probe.
    # probe variables
    variables = cms.PSet(
        pt     = cms.string("pt"),
        abseta = cms.string("abs(eta)"),
    ),
    # choice of what defines a 'passing' probe
    flags = cms.PSet(
        isIso = cms.InputTag("IsoMuons"),
    ),
    ## DATA-related info
    addRunLumiInfo = cms.bool(True),
    ## MC-related info
    isMC = cms.bool(False),
    motherPdgId = cms.vint32(22,23),
    makeMCUnbiasTree = cms.bool(True),
    checkMotherInUnbiasEff = cms.bool(True),
    tagMatches = cms.InputTag("muMcMatchTag"),
    probeMatches  = cms.InputTag("muMcMatchIDMuonProbe"),
    allProbes     = cms.InputTag("IDMuons"),
)

if process.tnpTree.isMC: 
   process.p = cms.Path(
                     process.taggedMuons
                     *process.triggerMatch
                     *process.tagMuons
                     *process.PFMuons
                     *process.IDMuons
                     *process.IsoMuons
                     *process.goodTracks
                     *process.trackCands
                     *process.trackProbes
                     *process.tkToPFMuons
                     *process.tkToIDMuons
                     *process.passingprobesForPFMuons
                     *process.passingprobesForIDMuons
                     *process.muMcMatchTag
                     *process.muMcMatchTrackProbe
                     *process.muMcMatchIDMuonProbe
                     *process.tagProbes
                     *process.tnpTree
                     *process.tagProbesIso
                     *process.tnpTreeIso
  )

else:
   process.p = cms.Path(
                     process.taggedMuons
                     *process.triggerMatch
                     *process.tagMuons
                     *process.PFMuons
                     *process.IDMuons
                     *process.IsoMuons
                     *process.goodTracks
                     *process.trackCands
                     *process.trackProbes
                     *process.tkToPFMuons
                     *process.tkToIDMuons
                     *process.passingprobesForPFMuons
                     *process.passingprobesForIDMuons
#                     *process.muMcMatchTag
#                     *process.muMcMatchTrackProbe
#                     *process.muMcMatchIDMuonProbe
                     *process.tagProbes
                     *process.tnpTree
                     *process.tagProbesIso
                     *process.tnpTreeIso
  )

