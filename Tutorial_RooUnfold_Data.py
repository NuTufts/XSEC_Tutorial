import numpy as np
import os
import ROOT

directory="XSEC_Tutorial_Outputs_Data/"
if not os.path.exists(directory):
    os.makedirs(directory)
def SAVEHIST(hist,filename,error=False):
    canv = ROOT.TCanvas('Can','Can',1000,642)
    if error:
        hist.Draw('HIST E')
    else:
        hist.Draw('HIST')
    canv.SaveAs(directory+filename+'.png')

def main():
    infile  = ROOT.TFile("XSEC_InputsFile_RooUnfold.root","READ")
    EventTree      = infile.Get('EventTree')
    Flux_h         = infile.Get('Neutrino_flux')
    Efficiency_h   = infile.Get('Run3_NuMu_CCQE_Selection_Efficiency')
    # Load Up Genie Predictions
    GeniePredicted_XSec      = infile.Get('numu_ccqe_xsec_mcc9_tuned_cv')
    GeniePredicted_XSec_low  = infile.Get('numu_ccqe_xsec_mcc9_genie_all_low')
    GeniePredicted_XSec_high = infile.Get('numu_ccqe_xsec_mcc9_genie_all_high;1')

    # I only put one entry in the tree. It holds ROOT Vector Objects
    Entrydata = EventTree.GetEntry(0)

    # Load in the ROOT Vectors of Energy, Genie Tune Weight, and POT Balancing Factor
    # Do this for Background Events, True Energy BnB CCQE Events.

    # Here, Background Events are made up of stuff in the 1m1p Final Selection from:
    # - BnB Overlay Non-CCQE NuMu Events (Regular and LowE Patch)
    # - Nue Intrinsic Events
    # - ExtBnB Events

    # Essentially, just every background you expect to be represented in data.
    # In theory we could add the dirt sample here as well.

    BackgroundEvents_Energy  = EventTree.BackgroundEvents_Energy
    BackgroundEvents_Weights = EventTree.BackgroundEvents_Weights
    BackgroundEvents_POT     = EventTree.BackgroundEvents_POT

    # The BnB CCQE True and Reco Energies come from all the Final 1m1p Selection
    # events that are CCQE NuMu in the BnB Overlay from both the regular and
    # low energy patch sample. We include several truth cuts to ensure the energy
    # and location are well reconstructed.Otherwise the events go in the Non-CCQE
    # Background Category.

    # Each event's truth energy, reconstructed energy, Genie Tune Weight, and POT
    # Balance factor are stored below. Note that the Reco & Truth Weight and POT
    # values are the same, and are included twice for easier understanding.

    CCQE_NuMu_True_Energy  = EventTree.BnBCCQE_True_Energy
    CCQE_NuMu_True_Weights = EventTree.BnBCCQE_True_Weights
    CCQE_NuMu_True_POT     = EventTree.BnBCCQE_True_POT

    CCQE_NuMu_Reco_Energy  = EventTree.BnBCCQE_Reco_Energy
    CCQE_NuMu_Reco_Weights = EventTree.BnBCCQE_Reco_Weights
    CCQE_NuMu_Reco_POT     = EventTree.BnBCCQE_Reco_POT

    # POT Balancing Factors for Data Events are all 1. Other factors are used to compare to the Data Scale.

    DataEvents_Energy = EventTree.DataEvents_Energy
    DataEvents_POT    = EventTree.DataEvents_POT
    Data_RUN3_POT     = 2.429524e20

    # Print out the vector sizes, telling us the stats of how many events we're dealing with.
    # Note that event weights, and POT Balancing Factors are not taken into account yet.
    print("Background Event Counts:", BackgroundEvents_Energy.size())
    print("CCQE_NuMu True Event Counts:", CCQE_NuMu_True_Energy.size())
    print("CCQE_NuMu Reco Event Counts:", CCQE_NuMu_Reco_Energy.size())
    print("Data       Event Counts:", DataEvents_Energy.size())

    # Let's put those into histograms.
    # Note that in choosing ranges of the histogram you should extend past
    # where you want your cross section to end, in order to account for unsmearing
    # events from reco energies higher than your upper limit.
    # For example, I want a cross section from 0-1000 MeV
    # so I use a range of 0-1500 MeV to be able to unfold events
    # that reco energies above their true energy down into my actual
    # range.
    Background_h = ROOT.TH1D("Background_h","Background_h",15,0,1500)
    Background_h.SetXTitle("Reco Neutrino Energy")
    Background_h.SetYTitle("Selected Background Events in 2.43e20")
    for i in range(BackgroundEvents_Energy.size()):
        Background_h.Fill(BackgroundEvents_Energy.at(i), BackgroundEvents_Weights.at(i)*BackgroundEvents_POT.at(i))

    CCQE_NuMu_True_h = ROOT.TH1D("CCQE_NuMu_True_h","CCQE_NuMu_True_h",15,0,1500)
    CCQE_NuMu_True_h.SetXTitle("True Neutrino Energy")
    CCQE_NuMu_True_h.SetYTitle("Selected CCQE_NuMu Events in 2.43e20")
    for i in range(CCQE_NuMu_True_Energy.size()):
        CCQE_NuMu_True_h.Fill(CCQE_NuMu_True_Energy.at(i), CCQE_NuMu_True_Weights.at(i)*CCQE_NuMu_True_POT.at(i))

    CCQE_NuMu_Reco_h = ROOT.TH1D("CCQE_NuMu_Reco_h","CCQE_NuMu_Reco_h",15,0,1500)
    CCQE_NuMu_Reco_h.SetXTitle("Reco Neutrino Energy")
    CCQE_NuMu_Reco_h.SetYTitle("Selected CCQE_NuMu Events in 2.43e20")
    for i in range(CCQE_NuMu_Reco_Energy.size()):
        CCQE_NuMu_Reco_h.Fill(CCQE_NuMu_Reco_Energy.at(i), CCQE_NuMu_Reco_Weights.at(i)*CCQE_NuMu_Reco_POT.at(i))

    Data_h = ROOT.TH1D("Data_h","Data_h",15,0,1500)
    Data_h.SetXTitle("Reco Neutrino Energy")
    Data_h.SetYTitle("Selected Data Events in 2.43e20")
    for i in range(DataEvents_Energy.size()):
        Data_h.Fill(DataEvents_Energy.at(i), DataEvents_POT.at(i))

    # Alright, let's extract a cross section.
    # Latex Format for XSEC Formula:
    #    \sigma_i = 22 \frac{\sum_{j} U(N_j-b_j)}{\epsilon_i\Phi_i N_t}
    #
    #  Or, more explicitly:
    #
    #
    # The CrossSection in Energy Bin i is calculated by:
    # 1) Taking the Data Events selected in reco energy bin j
    # 2) Subtracting away the background events in reco energy bin j.
    # 3) Take the remaining events, and 'unfold' (U) them in order
    # to undo the true->reco energy smearing, while summing up contributions
    # from all reco energy bins j. This is entirely handled by RooUnfold
    # 4) Next divide by the efficiency of selecting the signal event in
    # true energy bin i to get the number of signal events that occurred,
    # not just the ones we found.
    # 5) Divide by the (NuMu Flux)*(POT)*(Neutrons in Target) to get
    # Cross Section Per Neutron
    # 6) Multiply by 22 neutrons/argon to get Cross Section per Argon Nucleus
    # 7) Celebrate!!!

    """
    Steps 1 and 2: Subtract the Expected Background from the Data.
    This is done after the number of events has been scaled
    using tune weights and POT balancing
    """
    Data_Minus_Background_h = ROOT.TH1D("Data_Minus_Background_h","Data_Minus_Background_h",15,0,1500)
    Data_Minus_Background_h.SetXTitle("Reco Neutrino Energy")
    Data_Minus_Background_h.SetYTitle("Selected Data Minus Background Events in 2.43e20")
    for binx in range(Data_Minus_Background_h.GetNbinsX()):
        d = Data_h.GetBinContent(binx+1)
        b = Background_h.GetBinContent(binx+1)
        Data_Minus_Background_h.SetBinContent(binx+1,d-b)

    """
    Step 3: Now we do the unfolding. It's easy with RooUnfold.
    You'll use two parts, a response matrix, that gets fed the
    true and reco energies of the CCQE events so that it can
    learn the smearing. Then an unfolding procedure to use the
    response matrix on.
    """
    print("At this stage, I expect the program to fail in a moment \nif you have not sourced first_setup.sh, or do not have RooUnfold \nyou'll get AttributeError: RooUnfoldResponse")
    # We make the response matrix with the same binning as our other
    # histograms, though underneath the hood, I'm pretty sure its a
    # square 2d histogram with reco and true energies on the two axis.
    Response_Matrix = ROOT.RooUnfoldResponse (15, 0.0, 1500.0);
    # Then we feed the response matrix the CCQE NuMu MC Events:
    for i in range(CCQE_NuMu_Reco_Energy.size()):
        # Fill with (reco,true,weight)
        Response_Matrix.Fill(CCQE_NuMu_Reco_Energy.at(i), CCQE_NuMu_True_Energy.at(i), CCQE_NuMu_Reco_Weights.at(i))

    # Great, now that's filled, we can do the unfolding with ROOT.RooUnfoldMETHOD()
    # Note that RooUnfoldBayes() is the D'Agostini Method of unfolding
    iterations = 4
    RooUnfoldBayes_Data    = ROOT.RooUnfoldBayes(Response_Matrix, Data_Minus_Background_h, iterations);
    # Brief note: This tutorial uses Bayes/D'Agostini as the method of unfolding. RooUnfold features
    # two other methods of unfolding that can easily be substituted in: BinByBin Unfolding, and
    # Singular Value Decomposition (SVD) Unfolding:
    # kterm = 4
    # RooUnfoldBinByBin_Data    = ROOT.RooUnfoldBinByBin(Response_Matrix, Data_Minus_Background_h);
    # RooUnfoldSVD_Data         = ROOT.RooUnfoldSvd(Response_Matrix, Data_Minus_Background_h, kterm);


    # Now you finish up by grabbing the histogram of the unfolded data
    # 2 is kcovariance error propogation, 1 is binbybin error, and 0 is no error
    error_method = 2
    Unfolded_Data_Bayes_h  = RooUnfoldBayes_Data.Hreco(error_method)
    Unfolded_Data_Bayes_h.SetTitle("Bayes Unfolded CCQE 1m1p Signal")
    Unfolded_Data_Bayes_h.SetXTitle("Neutrino Energy")
    Unfolded_Data_Bayes_h.SetYTitle("Select Events in 2.43e20")

    """
    The remaining steps are just dividing by already calculated terms in the formula, so its really easy.
    But I'll throw in an explanation on how to actually get the terms so that you can duplicate this
    for your own measurement.

    1) Efficiency: This is somewhat tricky. Now that you've got selected data events in your XSEC Formula numerator
    in order to calculate the cross section you need to figure out how many of these types of events happened in
    the detector, not just the ones you found. To do this we want to divide by the total selection efficiency.
    I've precalculated this relative to this tutorial, because the process is not easily replicable in the python notebook.

    The Efficiency can just be calculated via:
    (All the CCQE NuMu Events in the Final Selection) / (All the CCQE NuMu Events in the MC you Generated)
    Note the numerator has to be a subset of the denominator. The numerator we have. That's the CCQE_Numu_True_Energy
    spectra we have above. The denominator I find by going as far back along the reco chain as I could, and counting
    up the CCQE NuMu events there, using the entire active volume (match neutron targets volume below). This is somewhat more challenging as pulling that information from upstream files is
    more difficult and slower than our final variable files. After that you just divide out to get the final selection
    efficiency.

    As a last note, the Efficiency should be in True Energy because the XSEC numerator has already been unfolded to
    represent the true energy signal, so we can divide by the true energy efficiency spectrum. Using Tune and POT weights
    for the efficiency is unnecessary as they should cancel out in the division.

    2) NuMu Flux: I got the NuMu flux from Jarrett. He handed by 60 numbers representing the flux in 50 MeV bins
    from 0->3000 MeV. I rebinned to 100MeV bins for what is stored in the files we load, to match the XSEC binning.
    I haven't checked the numbers yet, but according to Zarko, you can get the NuMu flux in root files at:
    /pnfs/uboone/persistent/uboonebeam/bnb_gsimple/bnb_gsimple_fluxes_01.09.2019_463_hist/

    3) POT: This is just the POT in the Data you are calculating a cross section from.

    4)Number of Neutrons in Target: We want the number of neutrons in the active volume:
    #n =  (ActiveVolume)*(DensitLiquidArgon)*(MolsPerGram)*(Avagadro'sNumber)*(NeutronsPerAtom)
    =   (256.25*233*1036.8 𝑐𝑚^3)  *   (1.3984 𝑔/𝑐𝑚3) * (1/39.95 𝑚𝑜𝑙/𝑔) * (6.022𝑒23 𝐴𝑟/𝑚𝑜𝑙)  * (22 𝑛/𝐴𝑟)
    = 2.87e31 Neutrons in Target

    5) Neutrons Per Argon: We use 22 for this.
    """
    neutron_targets = 2.87e31
    neutrons_per_argon = 22


    """
    Steps 4, 5 and 6: Let's put it all together and get a cross section!
    """
    # Note we are now resizing down to our desired 0-1000MeV Range for XSec
    # We are also going to stuff the order of magnitude (10^-38) into the yaxis
    # label in order to match the genie prediction plots I have attached.
    CrossSection_Bayes_h = ROOT.TH1D("CCQE_NuMu_Cross_Section_Bayes","CCQE_NuMu_Cross_Section_Bayes",10,0,1000)
    CrossSection_Bayes_h.SetXTitle("Neutrino Energy")
    CrossSection_Bayes_h.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon]")
    for binx in range(CrossSection_Bayes_h.GetNbinsX()):
        Efficiency  = Efficiency_h.GetBinContent(binx+1)
        Flux        = Flux_h.GetBinContent(binx+1)
        Denominator = 1.0*neutron_targets*Flux*Data_RUN3_POT*Efficiency
        Numerator   = Unfolded_Data_Bayes_h.GetBinContent(binx+1)
        XSec_Bayes  = 0.0
        err_Bayes   = Unfolded_Data_Bayes_h.GetBinError(binx+1)
        print(binx, err_Bayes, Efficiency)
        if Denominator !=0:
            # 1e38 is to put 1e-38 in the yaxis label
            XSec_Bayes = neutrons_per_argon*1E38*Numerator/Denominator
            err_Bayes  = neutrons_per_argon*1E38*err_Bayes/Denominator
            CrossSection_Bayes_h.SetBinContent(binx+1,XSec_Bayes)
            CrossSection_Bayes_h.SetBinError(binx+1,err_Bayes)


    """
    Step 7: Celebrate (And Make Plots)
    """
    ROOT.gStyle.SetOptStat(0);
    SAVEHIST(CrossSection_Bayes_h,"CrossSection_Bayes_h")
    SAVEHIST(Efficiency_h,"Efficiency_h")
    SAVEHIST(Flux_h,"Flux_h")
    SAVEHIST(Unfolded_Data_Bayes_h,"Unfolded_Data_Bayes_h")
    SAVEHIST(Data_Minus_Background_h,"Data_Minus_Background_h")
    SAVEHIST(Data_h,"Data_h")
    SAVEHIST(Background_h,"Background_h")
    SAVEHIST(CCQE_NuMu_True_h,"CCQE_NuMu_True_h")
    SAVEHIST(CCQE_NuMu_Reco_h,"CCQE_NuMu_Reco_h")

    # Swap to 1Gev from 1000Mev to Overlay on Genie prediction

    XSEC_Overlay_Bayes_h = ROOT.TH1D("CCQE_NuMu_Cross_Section_Bayes","CCQE_NuMu_Cross_Section_Bayes",10,0,1)
    XSEC_Overlay_Bayes_h.SetXTitle("Neutrino Energy")
    XSEC_Overlay_Bayes_h.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon]")
    XSEC_Overlay_Bayes_h.SetLineWidth(4)
    for binx in range(CrossSection_Bayes_h.GetNbinsX()):
        XSEC_Overlay_Bayes_h.SetBinContent(binx+1,CrossSection_Bayes_h.GetBinContent(binx+1))
        XSEC_Overlay_Bayes_h.SetBinError(binx+1,CrossSection_Bayes_h.GetBinError(binx+1))
    c1 = ROOT.TCanvas("canoe","canoe",1000,642)
    GeniePredicted_XSec_high.SetFillColor(ROOT.kGray)
    GeniePredicted_XSec_low.SetFillColor(10)
    GeniePredicted_XSec.SetFillColor(0)
    GeniePredicted_XSec_high.SetTitle("CCQE_NuMu_Cross_Section_Bayes")
    GeniePredicted_XSec_high.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon] ")
    GeniePredicted_XSec_low.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon] ")
    GeniePredicted_XSec.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon] ")
    XSEC_Overlay_Bayes_h.SetYTitle("Cross Section [10^{-38} cm^{2} / Argon] ")
    XSEC_Overlay_Bayes_h.SetLineWidth(4)
    GeniePredicted_XSec_high.Draw()
    GeniePredicted_XSec_low.Draw("SAME")
    GeniePredicted_XSec.Draw("SAME HIST")
    XSEC_Overlay_Bayes_h.Draw("SAME")
    ROOT.gPad.RedrawAxis()
    c1.SaveAs(directory+"XSEC_Overlaid.png")
    SAVEHIST(XSEC_Overlay_Bayes_h,"XSEC_Overlay_Bayes_h")


if __name__ == '__main__':
    main()
