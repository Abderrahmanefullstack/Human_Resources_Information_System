from django.db import models
from django.utils import timezone


class Agent(models.Model):
    Matricule = models.CharField(max_length=50, primary_key=True)
    Civilite = models.CharField(max_length=10)
    Nom = models.CharField(max_length=100)
    Prenom = models.CharField(max_length=100)
    NationaliteCode = models.CharField(max_length=10, null=True, blank=True)
    NationaliteLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateNaissance = models.DateField(null=True, blank=True)
    DateNaissanceCNSS = models.DateField(null=True, blank=True)
    AffectationLibelle = models.CharField(max_length=100, null=True, blank=True)
    AffectationCode = models.CharField(max_length=10, null=True, blank=True)
    SituationEffectifLibelle = models.CharField(max_length=100, null=True, blank=True)
    ArborescenceAffectation = models.CharField(max_length=500, null=True, blank=True)
    LieuNaissance = models.CharField(max_length=100, null=True, blank=True)
    SituationFamilleCode = models.CharField(max_length=10, null=True, blank=True)
    SituationFamilleLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateSituationFamille = models.DateField(null=True, blank=True)
    DroitPaie = models.BooleanField(null=True, blank=True)
    DateDeces = models.DateField(null=True, blank=True)
    DateCertificatDeces = models.DateField(null=True, blank=True)
    ChefDeFamille = models.BooleanField(null=True, blank=True)
    ConjointCPM = models.BooleanField(null=True, blank=True)
    NombreEnfants = models.IntegerField(null=True, blank=True)
    NombreEnfantsCharge = models.IntegerField(null=True, blank=True)
    NombreDeductions = models.IntegerField(null=True, blank=True)
    NoCIN = models.CharField(max_length=50, null=True, blank=True)
    DateExpirationCIN = models.DateField(null=True, blank=True)
    AutoriteDelivranceCIN = models.CharField(max_length=100, null=True, blank=True)
    NoPassePort = models.CharField(max_length=50, null=True, blank=True)
    DateDelivrancePassePort = models.DateField(null=True, blank=True)
    DateExpirationPassePort = models.DateField(null=True, blank=True)
    AutoriteDelivrancePassePort = models.CharField(
        max_length=100, null=True, blank=True
    )
    RegimeCNSS = models.CharField(max_length=100, null=True, blank=True)
    NoAffiliationCNSS = models.CharField(max_length=50, null=True, blank=True)
    DateAffiliationCNSS = models.DateField(null=True, blank=True)
    RegimeCIMR = models.CharField(max_length=100, null=True, blank=True)
    NoAffiliationCIMR = models.CharField(max_length=50, null=True, blank=True)
    DateAffiliationCIMR = models.DateField(null=True, blank=True)
    RegimeMUTUELLE = models.CharField(max_length=100, null=True, blank=True)
    NoAffiliationMUTUELLE = models.CharField(max_length=50, null=True, blank=True)
    TauxSurcotisationMutuelle = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    RegimeRCPCPM = models.CharField(max_length=100, null=True, blank=True)
    NoAffiliationRCPCPM = models.CharField(max_length=50, null=True, blank=True)
    MontantRETSA = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    StatutOrigine = models.CharField(max_length=100, null=True, blank=True)
    TypeContratLibelle = models.CharField(max_length=100, null=True, blank=True)
    TypeContratCode = models.CharField(max_length=10, null=True, blank=True)
    MotifEmbaucheLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateEntree = models.DateField(null=True, blank=True)
    DateDebutAdministration = models.DateField(null=True, blank=True)
    AncienneteSecteurBancaire = models.IntegerField(null=True, blank=True)
    NombreAnneesInterruption = models.IntegerField(null=True, blank=True)
    AncienneteAutresSecteurs = models.IntegerField(null=True, blank=True)
    AncienneteAcquiseCPM = models.IntegerField(null=True, blank=True)
    DateDebutAnciennete = models.DateField(null=True, blank=True)
    DateFinAdministration = models.DateField(null=True, blank=True)
    DateFinEffectif = models.DateField(null=True, blank=True)
    MotifDepartCode = models.CharField(max_length=10, null=True, blank=True)
    MotifDepartLibelle = models.CharField(max_length=100, null=True, blank=True)
    SituationEffectifCode = models.CharField(max_length=10, null=True, blank=True)
    DateDebutSituationEffectif = models.DateField(null=True, blank=True)
    DateFinSituationEffectif = models.DateField(null=True, blank=True)
    Indice = models.IntegerField(null=True, blank=True)
    DateEffetIndice = models.DateField(null=True, blank=True)
    ConventionCollectifCode = models.CharField(max_length=10, null=True, blank=True)
    ConventionCollectifLibelle = models.CharField(max_length=100, null=True, blank=True)
    ClasseCode = models.CharField(max_length=10, null=True, blank=True)
    ClasseLibelle = models.CharField(max_length=100, null=True, blank=True)
    EchelonCode = models.CharField(max_length=10, null=True, blank=True)
    EchelonLibelle = models.CharField(max_length=100, null=True, blank=True)
    CategorieCode = models.CharField(max_length=10, null=True, blank=True)
    CategorieLibelle = models.CharField(max_length=100, null=True, blank=True)
    GradeHierarchieCode = models.CharField(max_length=10, null=True, blank=True)
    GradeHierarchieLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateEffetGrade = models.DateField(null=True, blank=True)
    FonctionCode = models.CharField(max_length=10, null=True, blank=True)
    FonctionLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateEffetFonction = models.DateField(null=True, blank=True)
    EmploiCode = models.CharField(max_length=10, null=True, blank=True)
    EmploiLibelle = models.CharField(max_length=100, null=True, blank=True)
    LigneManagerialCode = models.CharField(max_length=10, null=True, blank=True)
    LigneManagerialLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateEffetLigneManagerial = models.DateField(null=True, blank=True)
    TypeActivite = models.CharField(max_length=100, null=True, blank=True)
    FonctionParInterimCode = models.CharField(max_length=10, null=True, blank=True)
    FonctionParInterimLibelle = models.CharField(max_length=100, null=True, blank=True)
    DateDebutFonctionParInterim = models.DateField(null=True, blank=True)
    DateFinFonctionParInterim = models.DateField(null=True, blank=True)
    NoteN = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    NoteN_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    NoteN_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    NotePrimeInteressement = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    NotePrimeBilan = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    NotePrimeProductivite = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    CentreResponsabilite = models.CharField(max_length=100, null=True, blank=True)
    CentreResponsabiliteOrigine = models.CharField(
        max_length=100, null=True, blank=True
    )
    DateDebutAffectation = models.DateField(null=True, blank=True)
    DateFinAffectation = models.DateField(null=True, blank=True)
    ClassificationAffectation = models.CharField(max_length=100, null=True, blank=True)
    MatriculeSuperieurHierarchiqueN1 = models.CharField(
        max_length=50, null=True, blank=True
    )
    NomPrenomSuperieurHierarchiqueN1 = models.CharField(
        max_length=200, null=True, blank=True
    )
    MatriculeSuperieurHierarchiqueN2 = models.CharField(
        max_length=50, null=True, blank=True
    )
    NomPrenomSuperieurHierarchiqueN2 = models.CharField(
        max_length=200, null=True, blank=True
    )
    LocalisationSite = models.CharField(max_length=100, null=True, blank=True)
    LocalisationVille = models.CharField(max_length=100, null=True, blank=True)
    LocalisationEtage = models.CharField(max_length=50, null=True, blank=True)
    LocalisationBureau = models.CharField(max_length=50, null=True, blank=True)
    TelephonePoste = models.CharField(max_length=50, null=True, blank=True)
    PortableGSMPro = models.CharField(max_length=50, null=True, blank=True)
    TelephoneSDA = models.CharField(max_length=50, null=True, blank=True)
    AdresseEmail = models.CharField(max_length=100, null=True, blank=True)
    MatriculeAssistante = models.CharField(max_length=50, null=True, blank=True)
    NomPrenomAssistante = models.CharField(max_length=200, null=True, blank=True)
    MatriculeFiliale = models.CharField(max_length=50, null=True, blank=True)
    DroitPointage = models.BooleanField(null=True, blank=True)
    EquipePointageCode = models.CharField(max_length=10, null=True, blank=True)
    EquipePointageLibelle = models.CharField(max_length=100, null=True, blank=True)
    GroupePointage = models.CharField(max_length=100, null=True, blank=True)
    Adresse = models.CharField(max_length=255, null=True, blank=True)
    Quartier = models.CharField(max_length=100, null=True, blank=True)
    Commune = models.CharField(max_length=100, null=True, blank=True)
    Region = models.CharField(max_length=100, null=True, blank=True)
    CodePostal = models.CharField(max_length=20, null=True, blank=True)
    Ville = models.CharField(max_length=100, null=True, blank=True)
    Pays = models.CharField(max_length=100, null=True, blank=True)
    TelephoneDomicile = models.CharField(max_length=50, null=True, blank=True)
    TelephonePortable = models.CharField(max_length=50, null=True, blank=True)
    EmailPersonnel = models.CharField(max_length=100, null=True, blank=True)
    ModePaiementCode = models.CharField(max_length=10, null=True, blank=True)
    ModePaiementLibelle = models.CharField(max_length=100, null=True, blank=True)
    CodeBanque = models.CharField(max_length=20, null=True, blank=True)
    CodeGuichet = models.CharField(max_length=20, null=True, blank=True)
    Generique = models.CharField(max_length=100, null=True, blank=True)
    Radical = models.CharField(max_length=100, null=True, blank=True)
    Plural = models.CharField(max_length=100, null=True, blank=True)
    CleControle = models.CharField(max_length=20, null=True, blank=True)
    NumeroCompte = models.CharField(max_length=50, null=True, blank=True)
    CleRib = models.CharField(max_length=20, null=True, blank=True)
    DevisePaiementCode = models.CharField(max_length=10, null=True, blank=True)
    DevisePaiementLibelle = models.CharField(max_length=100, null=True, blank=True)
    Domiciliation = models.BooleanField(null=True, blank=True)
    DateDebutDomiciliation = models.DateField(null=True, blank=True)
    DateFinDomiciliation = models.DateField(null=True, blank=True)
    NoteHierarchie = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    IndiceN_1 = models.CharField(max_length=50, null=True, blank=True)
    IndiceN_2 = models.CharField(max_length=50, null=True, blank=True)
    IndiceN_3 = models.CharField(max_length=50, null=True, blank=True)
    TauxPerformanceN_1 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    TauxPerformanceN_2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    TauxPerformanceN_3 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    # Bonification
    NombrePointsBonification = models.IntegerField(null=True, blank=True)
    DateEffetBonification = models.DateField(null=True, blank=True)

    # Primes / Indemnités (montants)
    PrimeTransport = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    PrimeLogement = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    FraisRepresentation = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    AideLogement = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    PrimeSpeciale = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    PrimeEmploi = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    IndemniteLoyer = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    IndemniteExpat = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    PrimeProvenceSahariale = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    MontantAugmentation = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    # Droits
    DroitPrimePanier = models.BooleanField(null=True, blank=True)

    # Totaux / Derniers montants
    BrutAnnuelTheorique = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    DernierBrutMensuel = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )
    NetAnnuelTheorique = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )
    DernierNetMensuel = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True
    )

    # Banque d’affectation
    BanqueAffectationCode = models.CharField(max_length=20, null=True, blank=True)
    BanqueAffectationLibelle = models.CharField(max_length=200, null=True, blank=True)
    NombrePointsAugmentationPromotionnelle = models.IntegerField(null=True, blank=True)
    MoisAvancement = models.CharField(max_length=20, null=True, blank=True)
    SalaireBase = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    MotifChangementCode = models.CharField(max_length=10, null=True, blank=True)
    MotifChangementLibelle = models.CharField(max_length=100, null=True, blank=True)
    NoteN_3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    IndiceN_4 = models.IntegerField(null=True, blank=True)
    TauxPerformanceN_3 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    BrutAnnuelTheoriqueDecN_1 = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    NetAnnuelTheoriqueDecN_1 = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    TotalAvantageDecN_1 = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    TotalRetenuesPrets = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )
    TotalAvantageMensuel = models.DecimalField(
        max_digits=18, decimal_places=2, null=True, blank=True
    )

    class Meta:
        managed = False  # IMPORTANT : on ne laisse pas Django créer la table
        db_table = "Agent"
        app_label = "agents"

    @property
    def sexe(self):
        """Propriété calculée pour le sexe basée sur la civilité"""
        if self.Civilite == "Mr":
            return "H"
        elif self.Civilite in ["Mme", "Mlle"]:
            return "F"
        return ""

    @property
    def matricule_formate(self):
        """Retourne le matricule sur 10 chiffres avec des zéros à gauche."""
        if self.Matricule:
            return str(self.Matricule).zfill(10)
        return ""

    @property
    def affectationCode_formate(self):
        """Retourne le matricule sur 10 chiffres avec des zéros à gauche."""
        if self.AffectationCode:
            return str(self.AffectationCode).zfill(6)
        return ""


class ImportLog(models.Model):
    filename = models.CharField(max_length=255)  # nom du fichier importé
    import_date = models.DateTimeField(default=timezone.now)  # date et heure

    def __str__(self):
        return f"{self.filename} - {self.import_date.strftime('%d/%m/%Y %H:%M')}"
