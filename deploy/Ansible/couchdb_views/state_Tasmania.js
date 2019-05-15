function (doc) {
  if (doc.state_code === 6)
    emit(doc._id, [doc.full_text, doc.state_name, doc.state_code, doc.polarity, doc.subjectivity, doc.LGA_code, doc.LGA_name]);
}