function (doc) {
  emit(doc._id, [doc.full_text, doc.state_name, doc.state_code, doc.polarity, doc.subjectivity]);
}