from pathlib import Path
import sys
import altair as alt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src.analysis import clean_data, load_data

st.set_page_config(page_title="BlinkIT | Grocery Performance", page_icon="🛒", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root{--ink:#18231f;--muted:#66736d}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:#f5f7f4;color:var(--ink)}
.block-container{padding-top:2rem;padding-bottom:2.5rem;max-width:1440px}
h1,h2,h3{font-family:'Manrope',sans-serif!important;letter-spacing:-.035em;color:var(--ink)}
[data-testid="stSidebar"]{background:#edf2ed;border-right:1px solid #dfe7df}
.hero{background:linear-gradient(115deg,#124c3b,#17664b 65%,#277855);color:white;padding:30px 34px;border-radius:22px;margin:0 0 22px;box-shadow:0 12px 30px #124c3b20;position:relative;overflow:hidden}
.hero:after{content:' ';position:absolute;width:250px;height:250px;border:1px solid #ffffff26;border-radius:50%;right:-42px;top:-105px;box-shadow:0 0 0 24px #ffffff09,0 0 0 50px #ffffff07}
.hero-kicker{font-size:.75rem;text-transform:uppercase;letter-spacing:.16em;color:#d6f3ad;font-weight:700;margin:0 0 7px}
.hero h1{color:white!important;font-size:2.15rem;line-height:1.15;margin:0 0 8px}.hero p{color:#dcebe3;margin:0;max-width:680px;font-size:.98rem}
.kpi{background:white;padding:17px 19px;border:1px solid #e6ece6;border-radius:16px;min-height:116px;box-shadow:0 3px 12px #14322309}
.kpi-label{color:var(--muted);font-size:.79rem;font-weight:600;margin-bottom:12px}.kpi-value{color:#18231f;font:700 1.65rem 'Manrope',sans-serif;letter-spacing:-.04em;line-height:1.1}.kpi-note{color:#849088;font-size:.75rem;margin-top:8px}
.section-title{font:700 1.18rem 'Manrope',sans-serif;margin:.2rem 0}.section-note{color:var(--muted);font-size:.86rem;margin:0 0 .8rem}
.insight{border-left:4px solid #77aa4a;padding:10px 13px;background:#eef5e9;border-radius:0 10px 10px 0;margin:.4rem 0;color:#304339;font-size:.9rem}
.small-muted{color:#77847c;font-size:.78rem}
</style>
""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading grocery data…")
def get_data():
    return clean_data(load_data(ROOT / "data" / "blinkit_grocery_data.xlsx"))

df = get_data()
FILTERS = ["Item Type", "Outlet Type", "Outlet Location Type", "Outlet Size", "Item Fat Content"]
OPTIONS = {c: sorted(df[c].dropna().unique().tolist()) for c in FILTERS}
with st.sidebar:
    st.markdown("## 🛒 BlinkIT")
    st.caption("Grocery performance explorer")
    st.divider()
    st.markdown("### Refine the view")
    if st.button("Reset all filters", use_container_width=True):
        for c in FILTERS:
            st.session_state[f"filter_{c}"] = []
        st.rerun()
    selected = {}
    for c in FILTERS:
        key=f"filter_{c}"
        if key not in st.session_state:
            st.session_state[key]=[]
        selected[c]=st.multiselect(c,OPTIONS[c],key=key,placeholder=f"All {c.lower()} values")
    st.divider()
    st.markdown("### About this view")
    st.caption("Each row is an item/outlet record. Sales totals depend on record counts; compare average sales per record alongside totals.")
    st.caption("The source workbook has no transaction dates or cost data.")

mask=pd.Series(True,index=df.index)
for c,values in selected.items():
    if values: mask &= df[c].isin(values)
f=df.loc[mask].copy()
st.markdown("""
<div class="hero"><div class="hero-kicker">Retail intelligence · Sapphire IQ</div>
<h1>Grocery performance, at a glance.</h1>
<p>Explore what sells, where performance concentrates, and how product and outlet patterns compare.</p></div>
""",unsafe_allow_html=True)
if f.empty:
    st.warning("No records match these filters. Select values in the sidebar or reset all filters.")
    st.stop()

cards=[("TOTAL RECORDED SALES",f"{f.Sales.sum():,.0f}",f"Across {len(f):,} filtered records"),("AVERAGE SALES / RECORD",f"{f.Sales.mean():,.2f}","A normalized performance view"),("AVERAGE CUSTOMER RATING",f"{f.Rating.mean():.2f} / 5","Mean rating in this selection"),("ITEM WEIGHT MISSING",f"{f['Item Weight'].isna().mean()*100:.1f}%","Data quality indicator")]
for start in (0,2):
    cols=st.columns(2,gap="medium")
    for col,(label,value,note) in zip(cols,cards[start:start+2]):
        col.markdown(f'<div class="kpi"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)
st.markdown("<div style='height:14px'></div>",unsafe_allow_html=True)

def styled(chart):
    return chart.configure_view(strokeOpacity=0).configure_axis(labelColor="#536159",titleColor="#536159",gridColor="#e7ece7",domainColor="#dce4dc",tickColor="#dce4dc",labelFont="DM Sans",titleFont="DM Sans").configure_title(font="Manrope",fontSize=15,color="#26352d",anchor="start")
overview,products,outlets=st.tabs(["Overview","Products","Outlets & signals"])
with overview:
    st.markdown("<div class='section-title'>Where sales add up</div><div class='section-note'>Compare total contribution with outlet mix. Hover over marks for exact values.</div>",unsafe_allow_html=True)
    left,right=st.columns([1.2,1],gap="large")
    cat=f.groupby("Item Type",as_index=False).agg(Sales=("Sales","sum"),Records=("Sales","size"),Mean=("Sales","mean")).sort_values("Sales")
    bars=alt.Chart(cat).mark_bar(cornerRadiusEnd=5,color="#17684b").encode(x=alt.X("Sales:Q",title="Recorded sales",axis=alt.Axis(format="~s")),y=alt.Y("Item Type:N",title=None,sort="-x"),tooltip=[alt.Tooltip("Item Type:N",title="Category"),alt.Tooltip("Sales:Q",format=",.0f"),alt.Tooltip("Records:Q",format=","),alt.Tooltip("Mean:Q",title="Mean / record",format=",.2f")]).properties(title="Sales by product category",height=350).interactive()
    loc=f.groupby("Outlet Location Type",as_index=False).agg(Sales=("Sales","sum"),Records=("Sales","size"),Mean=("Sales","mean"))
    locchart=alt.Chart(loc).mark_bar(cornerRadiusTopLeft=5,cornerRadiusTopRight=5).encode(x=alt.X("Outlet Location Type:N",title=None,sort=None),y=alt.Y("Sales:Q",title="Recorded sales",axis=alt.Axis(format="~s")),color=alt.Color("Outlet Location Type:N",title=None,scale=alt.Scale(range=["#155d45","#54a176","#b4db57"])),tooltip=["Outlet Location Type:N",alt.Tooltip("Sales:Q",format=",.0f"),alt.Tooltip("Records:Q",format=","),alt.Tooltip("Mean:Q",title="Mean / record",format=",.2f")]).properties(title="Sales by outlet location",height=350).interactive()
    with left: st.altair_chart(styled(bars),use_container_width=True)
    with right: st.altair_chart(styled(locchart),use_container_width=True)
    st.markdown("<div class='insight'>Read totals together with record counts and average sales per record. Larger groups can lead in total sales simply because they have more records.</div>",unsafe_allow_html=True)

with products:
    st.markdown("<div class='section-title'>What customers buy</div><div class='section-note'>Rank product categories, then compare item sales by product characteristic.</div>",unsafe_allow_html=True)
    left,right=st.columns([1.1,1],gap="large")
    cat=f.groupby("Item Type",as_index=False).agg(Sales=("Sales","sum"),Mean=("Sales","mean"),Records=("Sales","size")).sort_values("Sales",ascending=False)
    top=cat.head(10).sort_values("Sales")
    topchart=alt.Chart(top).mark_bar(color="#17684b",cornerRadiusEnd=5).encode(x=alt.X("Sales:Q",title="Recorded sales",axis=alt.Axis(format="~s")),y=alt.Y("Item Type:N",title=None,sort="-x"),tooltip=["Item Type:N",alt.Tooltip("Sales:Q",format=",.0f"),alt.Tooltip("Mean:Q",title="Mean / record",format=",.2f"),alt.Tooltip("Records:Q",format=",")]).properties(title="Top categories by recorded sales",height=350).interactive()
    box=alt.Chart(f).mark_boxplot(extent="min-max",size=42).encode(x=alt.X("Item Fat Content:N",title=None),y=alt.Y("Sales:Q",title="Sales per record"),color=alt.Color("Item Fat Content:N",title=None,scale=alt.Scale(range=["#17684b","#a8c96e"])),tooltip=["Item Fat Content:N",alt.Tooltip("Sales:Q",format=",.2f")]).properties(title="Sales distribution by fat content",height=350)
    with left: st.altair_chart(styled(topchart),use_container_width=True)
    with right: st.altair_chart(styled(box),use_container_width=True)
    table=cat.rename(columns={"Sales":"Total sales","Mean":"Mean sales / record","Records":"Records"})
    st.dataframe(table,hide_index=True,use_container_width=True,column_config={"Total sales":st.column_config.NumberColumn(format="%,.0f"),"Mean sales / record":st.column_config.NumberColumn(format="%,.2f")})

with outlets:
    st.markdown("<div class='section-title'>How outlets compare</div><div class='section-note'>View totals and per-record averages, then inspect product visibility signals.</div>",unsafe_allow_html=True)
    left,right=st.columns(2,gap="large")
    outlet=f.groupby("Outlet Type",as_index=False).agg(Sales=("Sales","sum"),Mean=("Sales","mean"),Records=("Sales","size"))
    totalchart=alt.Chart(outlet).mark_bar(color="#17684b",cornerRadiusTopLeft=5,cornerRadiusTopRight=5).encode(x=alt.X("Outlet Type:N",title=None,axis=alt.Axis(labelAngle=-20)),y=alt.Y("Sales:Q",title="Total sales",axis=alt.Axis(format="~s")),tooltip=["Outlet Type:N",alt.Tooltip("Sales:Q",format=",.0f"),alt.Tooltip("Records:Q",format=",")]).properties(title="Total sales by outlet type",height=320).interactive()
    meanchart=alt.Chart(outlet).mark_circle(size=120,color="#dc8543").encode(x=alt.X("Outlet Type:N",title=None,axis=alt.Axis(labelAngle=-20)),y=alt.Y("Mean:Q",title="Mean sales per record",scale=alt.Scale(zero=False)),tooltip=["Outlet Type:N",alt.Tooltip("Mean:Q",title="Mean / record",format=",.2f"),alt.Tooltip("Records:Q",format=",")]).properties(title="Average sales per record",height=320).interactive()
    with left: st.altair_chart(styled(totalchart),use_container_width=True)
    with right: st.altair_chart(styled(meanchart),use_container_width=True)
    scatter=alt.Chart(f).mark_circle(opacity=.45,size=55).encode(x=alt.X("Item Visibility:Q",title="Item visibility"),y=alt.Y("Sales:Q",title="Sales per record"),color=alt.Color("Outlet Type:N",title="Outlet type",scale=alt.Scale(scheme="greens")),tooltip=["Item Type:N","Outlet Identifier:N","Outlet Type:N",alt.Tooltip("Item Visibility:Q",format=".3f"),alt.Tooltip("Sales:Q",format=",.2f"),alt.Tooltip("Rating:Q",format=".1f")]).properties(title="Visibility and recorded sales",height=360).interactive()
    st.altair_chart(styled(scatter),use_container_width=True)
    corr=f[["Item Visibility","Sales"]].corr().iloc[0,1]
    st.markdown(f"<div class='insight'>In this filtered selection, visibility and sales have a Pearson correlation of <b>{corr:.3f}</b>. This descriptive statistic does not establish cause or rule out nonlinear patterns.</div>",unsafe_allow_html=True)
    st.markdown("#### Outlet detail")
    detail=f.groupby(["Outlet Identifier","Outlet Type","Outlet Location Type","Outlet Size"],as_index=False).agg(Total_sales=("Sales","sum"),Mean_sales_per_record=("Sales","mean"),Records=("Sales","size"),Mean_rating=("Rating","mean")).sort_values("Total_sales",ascending=False)
    st.dataframe(detail,hide_index=True,use_container_width=True,column_config={"Total_sales":st.column_config.NumberColumn("Total sales",format="%,.0f"),"Mean_sales_per_record":st.column_config.NumberColumn("Mean / record",format="%,.2f"),"Mean_rating":st.column_config.NumberColumn("Mean rating",format="%.2f")})

st.divider()
st.markdown("<div class='small-muted'>Source: supplied BlinkIT Grocery Data workbook · Descriptive analysis · No transaction dates or cost/margin fields are available</div>",unsafe_allow_html=True)
