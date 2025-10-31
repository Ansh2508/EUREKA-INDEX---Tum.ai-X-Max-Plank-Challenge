import { useState, useMemo } from 'react'
import './PriorArtTable.css'

function PriorArtTable({ patents = [], publications = [] }) {
  c